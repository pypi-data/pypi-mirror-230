from http import HTTPStatus

import flask
from flask import Blueprint, Response, current_app, request
from idpyoidc.client.oauth2 import Client
from perun.connector import Logger

from perun.proxygui.user_manager import UserManager

logger = Logger.get_logger(__name__)


def get_client(logout_cfg) -> Client:
    issuer = logout_cfg["key_conf"]["issuer_id"]
    client = current_app.rp_handler.init_client(issuer)
    client.client_id = logout_cfg["client_id"]

    return client


def construct_backchannel_logout_api_blueprint(cfg, logout_cfg):
    backchannel_logout_api = Blueprint("backchannel_logout_api", __name__)

    user_manager = UserManager(cfg)

    # Endpoints
    @backchannel_logout_api.route("/backchannel-logout/", methods=["POST"])
    def perform_backchannel_logout() -> Response:
        try:
            client = get_client(logout_cfg)
        except Exception as ex:
            error_message = f"Error happened while getting client: {ex}"
            logger.error(f"Exception: {error_message}")
            return Response(error_message, HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            try:
                sub, sid, issuer = current_app.rp_handler.backchannel_logout(
                    client, request_args=request.form
                )
                user_id = user_manager.sub_to_user_id(sub, issuer)

                if not user_id:
                    error_message = (
                        f"Could not fetch user ID for subject ID " f"'{sub}'"
                    )
                    return Response(error_message, HTTPStatus.INTERNAL_SERVER_ERROR)

                user_manager.logout(user_id=user_id, session_id=sid)

            except Exception as ex:
                error_message = (
                    f"Error happened while performing backchannel logout: '" f"{ex}'!"
                )
                logger.error(f"Exception: {error_message}")
                return Response(error_message, HTTPStatus.BAD_REQUEST)

        response = flask.Response()
        response.headers["Cache-Control"] = "no-store"
        response.status_code = HTTPStatus.NO_CONTENT

        return response

    return backchannel_logout_api
