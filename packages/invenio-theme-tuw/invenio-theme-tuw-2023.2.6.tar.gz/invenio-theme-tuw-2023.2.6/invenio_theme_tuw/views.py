# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""TU Wien theme for Invenio (RDM)."""

import requests
from flask import Blueprint, abort, current_app, g, render_template, request
from flask_login import current_user, login_required
from invenio_accounts.models import User
from invenio_app_rdm.records_ui.views.deposits import deposit_create, deposit_edit
from invenio_cache import current_cache
from invenio_communities.proxies import current_communities
from invenio_communities.views.communities import communities_new
from invenio_mail.tasks import send_email
from invenio_rdm_records.proxies import current_rdm_records_service as rec_service
from invenio_rdm_records.resources.serializers import UIJSONSerializer
from sqlalchemy.exc import NoResultFound

from .search import FrontpageRecordsSearch


def fetch_schemaorg_jsonld(doi_url):
    """Fetch the Schema.org metadata for the DOI."""
    key = f"schemaorg_{doi_url}"
    metadata = current_cache.get(key)

    if metadata is None:
        try:
            response = requests.get(
                doi_url,
                headers={"Accept": "application/vnd.schemaorg.ld+json"},
                timeout=2,
            )
            if response.status_code == 200:
                metadata = response.text.strip()
                current_cache.set(key, metadata)

        except Exception as e:
            current_app.logger.warning(
                f"Exception while fetching JSON-LD metadata: {e}"
            )

    return metadata


@login_required
def guarded_deposit_create(*args, **kwargs):
    """Guard the creation page for records, based on permissions."""
    if not rec_service.check_permission(g.identity, "create"):
        return render_template(
            "invenio_theme_tuw/guards/deposit.html", user=current_user
        )

    return deposit_create(*args, **kwargs)


@login_required
def guarded_deposit_edit(*args, **kwargs):
    """Guard the edit page for records, based on permissions."""
    # NOTE: this extra loading of the draft introduces an extra DB query, but i think
    #       it should not make too much of a difference for us
    draft = rec_service.draft_cls.pid.resolve(
        kwargs["pid_value"], registered_only=False
    )
    if not rec_service.check_permission(g.identity, "update_draft", record=draft):
        return render_template(
            "invenio_theme_tuw/guards/deposit.html", user=current_user
        )

    return deposit_edit(*args, **kwargs)


@login_required
def guarded_communities_create(*args, **kwargs):
    """Guard the communities creation page, based on permissions."""
    if not current_communities.service.check_permission(g.identity, "create"):
        return render_template(
            "invenio_theme_tuw/guards/community.html", user=current_user
        )

    return communities_new(*args, **kwargs)


def resolve_record(recid):
    """Resolve the record with the given recid into an API class object."""
    try:
        return rec_service.record_cls.pid.resolve(recid, registered_only=False)
    except NoResultFound:
        # if no record can be found for the ID, let's try if we can find a draft
        # (e.g. in the case of a draft preview)
        #
        # note: `invenio_pidstore.errors` contains further exceptions that could
        #       be raised during the PID resolution
        return rec_service.draft_cls.pid.resolve(recid, registered_only=False)


def resolve_first_user_owner(record):
    """Resolve the first user-type owner of the record.

    The record is expected to be an API-class object, and the result will be a User
    model object.
    """
    owners = record.parent.access.owners or []
    user_owners = [owner for owner in owners if owner.owner_type == "user"]

    if not user_owners:
        return None

    return user_owners[0].resolve()


def get_name_of_user_owner(owner):
    """Resolve the user referenced by the owner object and get their full name."""
    user_id = owner["user"]
    return User.query.get(user_id).user_profile.get("full_name")


def create_blueprint(app):
    """Create a blueprint with routes and resources."""

    blueprint = Blueprint(
        "invenio_theme_tuw",
        __name__,
        template_folder="theme/templates",
        static_folder="theme/static",
    )

    @blueprint.app_template_filter("tuw_doi_identifier")
    def tuw_doi_identifier(identifiers):
        """Extract DOI from sequence of identifiers."""
        if identifiers is not None:
            for identifier in identifiers:
                if identifier.get("scheme") == "doi":
                    return identifier.get("identifier")

    @blueprint.app_template_global("tuw_create_schemaorg_metadata")
    def tuw_create_schemaorg_metadata(record):
        """Create schema.org metadata to include in a <script> tag."""
        metadata = None

        # get the DOI from the managed PIDs, or from the metadata as fallback
        rec_pids = record.get("pids", {})
        if "doi" in rec_pids:
            doi = rec_pids["doi"].get("identifier")
        else:
            rec_meta = record.get("metadata", {})
            doi = tuw_doi_identifier(rec_meta.get("identifiers"))

        if doi is not None:
            doi_url = (
                doi if doi.startswith("https://") else ("https://doi.org/%s" % doi)
            )
            metadata = fetch_schemaorg_jsonld(doi_url)

        return metadata

    @blueprint.app_template_global("record_count")
    def record_count():
        return FrontpageRecordsSearch().count()

    @blueprint.route("/")
    def tuw_index():
        """Custom landing page showing the latest 5 records."""
        records = FrontpageRecordsSearch()[:5].sort("-created").execute()
        return render_template(
            "invenio_theme_tuw/overrides/frontpage.html",
            records=_records_serializer(records),
        )

    def _records_serializer(records=None):
        """Serialize list of records."""
        record_list = []
        for record in records or []:
            record_list.append(UIJSONSerializer().dump_obj(record.to_dict()))
        return record_list

    @blueprint.route("/tuw/contact-uploader/<recid>", methods=["GET", "POST"])
    def contact_uploader(recid):
        """Contact page for the contact's uploader."""
        captcha = current_app.extensions["invenio-theme-tuw"].captcha
        record = resolve_record(recid)
        form_values = request.form.to_dict()
        if current_user and not current_user.is_anonymous:
            form_values.setdefault("name", current_user.user_profile.get("full_name"))
            form_values.setdefault("email", current_user.email)

        if record is None:
            abort(404)

        owners = record.parent.access.owned_by
        if not owners:
            abort(404)

        owner = owners[0].resolve()

        submitted = False
        captcha_failed = False
        if request.method == "POST":
            # NOTE: the captcha is a simple spam prevention measure, and it also
            #       prevents the form from being accidentally resubmitted wia refresh
            if not current_app.config["CAPTCHA_ENABLE"] or captcha.validate():
                sitename = current_app.config["THEME_SITENAME"]
                sender_name = request.form["name"]
                sender_email = request.form["email"]
                inquiry = request.form["message"] or "<Empty Message>"
                html_message = render_template(
                    "invenio_theme_tuw/contact_mail_html.jinja",
                    sender_name=sender_name,
                    sender_email=sender_email,
                    message=inquiry,
                    uploader=owner,
                    record=record,
                )
                message = render_template(
                    "invenio_theme_tuw/contact_mail_text.jinja",
                    sender_name=sender_name,
                    sender_email=sender_email,
                    message=inquiry,
                    uploader=owner,
                    record=record,
                )

                add_sender_to_cc = current_app.config.get(
                    "THEME_TUW_CONTACT_UPLOADER_ADD_EMAIL_TO_CC", False
                )
                record_title = record.metadata["title"]
                send_email(
                    {
                        "subject": f'{sitename}: Inquiry about your record "{record_title}" from {sender_name}',
                        "html": html_message,
                        "body": message,
                        "recipients": [owner.email],
                        "cc": [sender_email] if add_sender_to_cc else [],
                        "reply_to": sender_email,
                    }
                )

                submitted = True

            else:
                captcha_failed = True

        response = render_template(
            "invenio_theme_tuw/contact_uploader.html",
            uploader=owner,
            submitted=submitted,
            record=record,
            captcha_failed=captcha_failed,
            form_values=form_values,
        )
        return response, 200 if not captcha_failed else 428

    @blueprint.route("/tuw/policies")
    def tuw_policies():
        """Page showing the available repository policies."""
        return render_template("invenio_theme_tuw/policies.html")

    @blueprint.route("/tuw/terms-of-use")
    def tuw_terms_of_use():
        """Page showing the repository's terms of use documents."""
        return render_template("invenio_theme_tuw/terms_of_use.html")

    @blueprint.route("/tuw/contact")
    def tuw_contact():
        """Contact page."""
        return render_template("invenio_theme_tuw/contact.html")

    @blueprint.route("/tuwstones/florian.woerister")
    def tuw_tombstone_florian():
        """Tombstone page for Florian Wörister."""
        return render_template("invenio_theme_tuw/tuwstones/florian_woerister.html")

    @app.before_first_request
    def override_deposit_pages():
        """Override the existing view functions with more access control."""

        # we have some additional role-based permissions (trusted-user) that decide
        # among other things if people can create records/drafts
        # this is not considered in the original view functions, which is why we
        # currently need to wrap them with our own guards
        app.view_functions[
            "invenio_app_rdm_records.deposit_edit"
        ] = guarded_deposit_edit
        app.view_functions[
            "invenio_app_rdm_records.deposit_create"
        ] = guarded_deposit_create
        app.view_functions[
            "invenio_communities.communities_new"
        ] = guarded_communities_create

        # limit the amount of contact requests that can be made per time period
        # (this needs to be done after the Flask-Limiter extension has been init.)
        limiter = app.extensions["limiter"]
        limit_value = app.config.get("THEME_TUW_CONTACT_UPLOADER_RATE_LIMIT", "5/hour")
        contact_uploader_view_func = app.view_functions[
            "invenio_theme_tuw.contact_uploader"
        ]
        app.view_functions["invenio_theme_tuw.contact_uploader"] = limiter.limit(
            limit_value, methods=["POST"]
        )(contact_uploader_view_func)

    # register filters for showing uploaders
    blueprint.add_app_template_filter(resolve_record)
    blueprint.add_app_template_filter(resolve_first_user_owner)

    return blueprint
