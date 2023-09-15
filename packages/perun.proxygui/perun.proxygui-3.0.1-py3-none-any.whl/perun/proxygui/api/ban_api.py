import gzip
import io
import json
import tarfile
from http import HTTPStatus

import flask
from bson.json_util import dumps
from flask import Blueprint, request, Response
from perun.connector import Logger
from pymongo.collection import Collection

from perun.proxygui.user_manager import UserManager

logger = Logger.get_logger(__name__)


def get_ban_collection(user_manager: UserManager) -> Collection:
    return user_manager.database_service.get_mongo_db_collection("ban_database")


def is_ban_in_db(ban_id: int, ban_collection: Collection) -> bool:
    return ban_collection.find_one({"id": ban_id}) is not None


def remove_outdated_bans_from_db(banned_users, ban_collection: Collection):
    current_ban_ids = [ban["id"] for ban in banned_users.values()]
    ban_collection.delete_many({"id": {"$nin": current_ban_ids}})


def construct_ban_api_blueprint(cfg):
    ban_api = Blueprint("ban_api", __name__)

    USER_MANAGER = UserManager(cfg)
    UPLOAD_FILE_MAX_SIZE = int(cfg.get("max_ban_upload_filesize"))

    # Endpoints
    @ban_api.route("/banned-users/", methods=["PUT"])
    def update_banned_users() -> Response:
        process_update(request.get_json())

        response = flask.Response()
        response.headers["Cache-Control"] = "public, max-age=0"
        response.status_code = HTTPStatus.NO_CONTENT

        return response

    @ban_api.route("/banned-users-generic/", methods=["PUT"])
    def update_banned_users_generic() -> Response:
        if request.content_length > UPLOAD_FILE_MAX_SIZE:
            logger.warn(
                f"Request too large: "
                f"{str((request.content_length // 1024) // 1024)} MB"
            )
            response = flask.make_response(
                "Request too large!", HTTPStatus.REQUEST_ENTITY_TOO_LARGE
            )
            response.headers["Cache-Control"] = "public, max-age=0"
            return response

        banned_users = None
        banned_users_tar_filepath = "./banned_facility_users"
        io_bytes = io.BytesIO(request.get_data())
        gzip_file = gzip.GzipFile(fileobj=io_bytes)
        try:
            with tarfile.open(fileobj=gzip_file) as tar:
                for tarinfo in tar:
                    if tarinfo.isreg() and tarinfo.name == banned_users_tar_filepath:
                        ban_file = tarinfo.path
                        with tar.extractfile(ban_file) as f:
                            content = f.read()
                            banned_users = json.loads(content)
        except Exception as ex:
            logger.warn("Could not parse banned users data: ", ex)
            return flask.make_response(
                f"Could not parse banned users data: {ex}",
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )

        if banned_users is None:
            logger.warn("Banned users file not found in the request.")
            response = flask.make_response(
                "Banned users file not found in the request.",
                HTTPStatus.UNPROCESSABLE_ENTITY,
            )
            response.headers["Cache-Control"] = "public, max-age=0"
            return response

        process_update(banned_users)

        logger.info("Banned users successfully updated.")
        response = flask.Response()
        response.headers["Cache-Control"] = "public, max-age=0"
        response.status_code = HTTPStatus.NO_CONTENT
        return response

    def process_update(banned_users) -> None:
        ban_collection = get_ban_collection(USER_MANAGER)

        remove_outdated_bans_from_db(banned_users, ban_collection)

        for user_id, ban in banned_users.items():
            if not is_ban_in_db(int(ban["id"]), ban_collection):
                USER_MANAGER.logout(user_id=user_id, include_refresh_tokens=True)
            ban_collection.replace_one({"id": ban["id"]}, ban, upsert=True)
        logger.debug(f"User bans updated: {dumps(ban_collection.find())}")

    @ban_api.route("/ban/<ban_id>", methods=["GET"])
    def find_ban(ban_id: str) -> str:
        ban_collection = get_ban_collection(USER_MANAGER)
        found_ban = ban_collection.find_one({"id": int(ban_id)})

        return dumps(found_ban) if found_ban else dumps({})

    return ban_api
