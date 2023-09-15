import copy
from uuid import uuid4

import flask
import yaml
from flask import Blueprint, request, url_for
from flask import render_template, make_response, jsonify, session
from flask_babel import gettext, get_locale
from flask_pyoidc.user_session import UserSession

from perun.proxygui.jwt import JWTService
from perun.proxygui.user_manager import UserManager
from perun.utils.consent_framework.consent_manager import ConsentManager


def ignore_claims(ignored_claims, claims):
    result = dict()

    for claim in claims:
        if claim not in ignored_claims:
            result[claim] = claims[claim]

    return result


def construct_gui_blueprint(cfg, auth):
    gui = Blueprint("gui", __name__, template_folder="templates")
    consent_db_manager = ConsentManager(cfg)
    user_manager = UserManager(cfg)
    jwt_service = JWTService(cfg)

    REDIRECT_URL = cfg["redirect_url"]
    COLOR = cfg["bootstrap_color"]
    OIDC_CFG = cfg["oidc_provider"]

    @gui.route("/authorization/<token>")
    def authorization(token):
        message = jwt_service.verify_jwt(token)
        email = message.get("email")
        service = message.get("service")
        registration_url = message.get("registration_url")
        if not email or not service:
            return make_response(
                jsonify({gettext("fail"): gettext("Missing request parameter")}),
                400,
            )
        return render_template(
            "authorization.html",
            email=email,
            service=service,
            registration_url=registration_url,
            bootstrap_color=COLOR,
        )

    @gui.route("/SPAuthorization/<token>")
    def sp_authorization(token):
        message = jwt_service.verify_jwt(token)
        email = message.get("email")
        service = message.get("service")
        registration_url = message.get("registration_url")
        return render_template(
            "SPAuthorization.html",
            email=email,
            service=service,
            registration_url=registration_url,
            bootstrap_color=COLOR,
        )

    @gui.route("/IsTestingSP")
    def is_testing_sp():
        return render_template(
            "IsTestingSP.html",
            redirect_url=REDIRECT_URL,
            bootstrap_color=COLOR,
        )

    @gui.route("/consent/<token>")
    def consent(token):
        ticket = jwt_service.verify_jwt(token)
        data = consent_db_manager.fetch_consent_request(ticket)
        if not ticket:
            return make_response(
                jsonify({gettext("fail"): gettext("received invalid ticket")}),
                400,
            )

        months_valid = cfg["consent"]["months_valid"]
        session["id"] = data["id"]
        session["state"] = uuid4().urn
        session["redirect_endpoint"] = data["redirect_endpoint"]
        session["attr"] = ignore_claims(cfg["consent"]["ignored_claims"], data["attr"])
        session["user_id"] = data["user_id"]
        session["locked_attrs"] = data.get("locked_attrs")
        session["requester_name"] = data["requester_name"]
        session["month"] = months_valid

        warning = cfg["consent"].get("warning", None)
        with open(
            cfg["consent"]["attribute_config_path"],
            "r",
            encoding="utf8",
        ) as ymlfile:
            attr_config = yaml.safe_load(ymlfile)

        return render_template(
            "ConsentRegistration.html",
            bootstrap_color=COLOR,
            cfg=cfg,
            attr_config=attr_config,
            released_claims=copy.deepcopy(session["attr"]),
            locked_claims=session["locked_attrs"],
            requester_name=session["requester_name"],
            months=months_valid,
            data_protection_redirect=data["data_protection_redirect"],
            warning=warning,
        )

    @auth.oidc_auth(OIDC_CFG["provider_name"])
    @gui.route("/mfa-reset-verify/<token>")
    def mfa_reset_verify(token):
        reset_request = jwt_service.verify_jwt(token)
        if reset_request:
            requester_email = reset_request.get("requester_email")
            user_manager.forward_mfa_reset_request(requester_email)
            return render_template(
                "MfaResetVerifyConfirmationSuccess.html",
            )
        else:
            return render_template(
                "MfaResetVerifyConfirmationFail.html",
            )

    @auth.oidc_auth(OIDC_CFG["provider_name"])
    @gui.route("/send-mfa-reset-emails")
    def send_mfa_reset_emails():
        user_session = UserSession(flask.session)
        sub = user_session.userinfo.get("sub")
        issuer = OIDC_CFG["issuer"]
        user_id = user_manager.sub_to_user_id(sub, issuer)
        locale = get_locale().language
        preferred_email = user_manager.handle_mfa_reset(
            user_id, locale, url_for("gui.mfa_reset_verify")
        )
        return render_template(
            "MfaResetEmailSent.html",
            email=preferred_email,
        )

    @auth.oidc_auth(OIDC_CFG["provider_name"])
    @gui.route("/mfa-reset")
    def mfa_reset():
        return render_template(
            "MfaResetInitiated.html",
            redirect_url=REDIRECT_URL,
            bootstrap_color=COLOR,
            referrer=request.referrer or "/",
            send_mfa_reset_emails=url_for("gui.send_mfa_reset_emails"),
        )

    return gui
