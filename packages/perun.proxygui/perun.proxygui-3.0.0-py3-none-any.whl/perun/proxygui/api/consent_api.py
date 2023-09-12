from http import HTTPStatus

from authlib.integrations.flask_oauth2 import current_token
from flask import (
    Blueprint,
    request,
    jsonify,
    abort,
    session,
    redirect,
    Response,
)
from perun.connector import Logger

from perun.proxygui.jwt import JWTService
from perun.proxygui.oauth import require_oauth
from perun.proxygui.user_manager import UserManager
from perun.utils.consent_framework.consent import Consent
from perun.utils.consent_framework.consent_manager import (
    ConsentManager,
    InvalidConsentRequestError,
)

logger = Logger.get_logger(__name__)


def construct_consent_api(cfg):
    consent_api = Blueprint("consent_framework", __name__)
    db_manager = ConsentManager(cfg)
    user_manager = UserManager(cfg)
    jwt_service = JWTService(cfg)

    oauth_cfg = cfg["oidc_provider"]

    @consent_api.route("/verify/<consent_id>")
    def verify(consent_id):
        attrs = db_manager.fetch_consented_attributes(consent_id)
        if attrs:
            return jsonify(attrs)

        logger.debug("no consent found for id '%s'", consent_id)
        abort(401)

    @consent_api.route("/creq/<jwt>", methods=["GET", "POST"])
    def creq(jwt):
        if request.method == "POST":
            jwt = request.values.get("jwt")
        try:
            jwt = jwt_service.verify_jwt(jwt)
            ticket = db_manager.save_consent_request(jwt)
            return ticket
        except InvalidConsentRequestError as e:
            logger.debug("received invalid consent request: %s, %s", str(e), jwt)
            abort(400)

    @consent_api.route("/save_consent")
    def save_consent():
        state = request.args["state"]
        validation = "validation" in request.args
        consent_status = request.args["consent_status"]
        requester = session["requester_name"]
        user_id = session["user_id"]
        redirect_uri = session["redirect_endpoint"]
        month = request.args["month"]

        attributes = request.args.to_dict()
        if "validation" in attributes:
            attributes.pop("validation")
        attributes.pop("consent_status")
        attributes.pop("state")
        attributes.pop("month")

        for attr in session["locked_attrs"]:
            attributes[attr] = session["attr"][attr]

        if state != session["state"]:
            abort(403)
        if consent_status == "yes" and not set(attributes).issubset(
            set(session["attr"])
        ):
            abort(400)

        if consent_status == "yes" and validation:
            consent = Consent(attributes, user_id, requester, int(month))
            db_manager.save_consent(session["id"], consent)
            session.clear()

        if consent_status == "no":
            return redirect(cfg["redirect_url"])
        return redirect(redirect_uri)

    # scopes in form ['scope1 scope2'] represent logical conjunction in Authlib
    required_scopes = [" ".join(oauth_cfg["scopes"])]

    @consent_api.route("/users/me/consents", methods=["GET"])
    @require_oauth(required_scopes)
    def consents():
        scopes = current_token.scopes
        sub = scopes.get("sub")
        issuer = cfg["oidc_provider"]["issuer"]
        user_id = user_manager.sub_to_user_id(sub, issuer)
        if not user_id:
            error_message = f"Could not fetch user ID for subject ID '{sub}'"
            return Response(error_message, HTTPStatus.INTERNAL_SERVER_ERROR)

        user_consents = db_manager.fetch_all_user_consents(user_id)
        return jsonify(user_consents)

    @consent_api.route("/users/me/consents/<consent_id>", methods=["DELETE"])
    @require_oauth(required_scopes)
    def delete_consent(consent_id):
        deleted_count = db_manager.delete_user_consent(consent_id)
        print("deleted_count", deleted_count)

        if deleted_count > 0:
            return jsonify(
                {
                    "deleted": "true",
                    "message": f"Successfully deleted consent with id {consent_id}",
                }
            )
        else:
            return jsonify(
                {
                    "deleted": "false",
                    "message": f"Requested consent with id {consent_id} "
                    f"was not deleted because it was not found in "
                    f"the database.",
                }
            )

    return consent_api
