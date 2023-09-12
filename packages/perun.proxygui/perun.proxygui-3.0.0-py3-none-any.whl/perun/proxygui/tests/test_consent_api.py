import json
from functools import wraps
from http import HTTPStatus
from unittest.mock import patch, Mock

import pytest

from perun.proxygui.api import consent_api
from perun.proxygui.app import get_flask_app, get_config
from perun.proxygui.tests.shared_test_data import SHARED_TESTING_CONFIG, ATTRS_MAP


# decorator that acts as a passthrough function
def mock_decorator(*args, **kwargs):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            return func(*args, **kwargs)

        return decorated_function

    return decorator


# bypass authentication by mocking auth decorator and its configuration
patch("perun.proxygui.api.consent_api.require_oauth", mock_decorator).start()
patch("perun.proxygui.app.configure_resource_protector", lambda x: x).start()


@pytest.fixture()
def app():
    with patch(
        "perun.utils.ConfigStore.ConfigStore.get_global_cfg",
        return_value=SHARED_TESTING_CONFIG,
    ), patch(
        "perun.utils.ConfigStore.ConfigStore.get_attributes_map",
        return_value=ATTRS_MAP,
    ):
        cfg = get_config()
        app = get_flask_app(cfg)
        app.config["TESTING"] = True
        yield app


USERS_CONSENTS_IN_DB = ["consent1", "consent2"]


def test_verify_endpoint(app):
    client = app.test_client()

    with patch(
        "perun.utils.consent_framework.consent_manager."
        "ConsentManager.fetch_consented_attributes",
        return_value={"attr1": "value1", "attr2": "value2"},
    ):
        response = client.get("/verify/consent_id")
    assert response.status_code == HTTPStatus.OK
    assert response.get_json() == {"attr1": "value1", "attr2": "value2"}

    with patch(
        "perun.utils.consent_framework.consent_manager."
        "ConsentManager.fetch_consented_attributes",
        return_value=None,
    ):
        response = client.get("/verify/consent_id")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_save_consent_endpoint(app):
    client = app.test_client()

    with client.session_transaction() as session:
        session["state"] = "state"
        session["attr"] = {"attr1": "value1", "attr2": "value2"}
        session["locked_attrs"] = []
        session["id"] = "id"
        session["user_id"] = "user_id"
        session["requester_name"] = "requester_name"
        session["redirect_endpoint"] = "/redirect"

    with patch(
        "perun.utils.consent_framework.consent_manager.ConsentManager.save_consent"
    ):
        response = client.get(
            "/save_consent?state=state&validation=true&consent_"
            "status=yes&month=6&attr1=value1&attr2=value2"
        )
    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["Location"] == "/redirect"

    with client.session_transaction() as session:
        session["state"] = "state"
        session["attr"] = {"attr1": "value1", "attr2": "value2"}
        session["locked_attrs"] = []
        session["id"] = "id"
        session["user_id"] = "user_id"
        session["requester_name"] = "requester_name"
        session["redirect_endpoint"] = "/redirect"

    with patch(
        "perun.utils.consent_framework.consent_manager.ConsentManager.save_consent"
    ):
        response = client.get(
            "/save_consent?state=invalid_state&validation=true&consent_"
            "status=yes&month=6&attr1=value1&attr2=value2"
        )
    assert response.status_code == HTTPStatus.FORBIDDEN

    with patch(
        "perun.utils.consent_framework.consent_manager.ConsentManager.save_consent"
    ):
        response = client.get(
            "/save_consent?state=state&validation=true&consent_status="
            "yes&month=6&attr1=value1&attr3=value3"
        )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_delete_consent_endpoint(app):
    client = app.test_client()
    # successful delete of a single existing consent
    with patch(
        "perun.utils.consent_framework.consent_manager.ConsentManager"
        ".delete_user_consent",
        return_value=1,
    ):
        REAL_CONSENT_ID = "real_consent_id"
        response = client.delete(f"/users/me/consents/{REAL_CONSENT_ID}")
        response_json = json.loads(response.data)
    CONSENT_DELETE_SUCCESS_MSG = (
        f"Successfully deleted consent with id {REAL_CONSENT_ID}"
    )

    assert CONSENT_DELETE_SUCCESS_MSG in str(response_json["message"])
    assert response_json["deleted"] == "true"

    # unsuccessful delete of a single non-existing consent
    with patch(
        "perun.utils.consent_framework.consent_manager.ConsentManager"
        ".delete_user_consent",
        return_value=0,
    ):
        FAKE_CONSENT_ID = "fake_consent_id"
        response = client.delete(f"/users/me/consents/{FAKE_CONSENT_ID}")
        response_json = json.loads(response.data)
    CONSENT_DELETE_FAILED_MSG = (
        f"Requested consent with id {FAKE_CONSENT_ID} was not "
        f"deleted because it was not found in the database."
    )

    assert CONSENT_DELETE_FAILED_MSG in str(response_json["message"])
    assert response_json["deleted"] == "false"


def test_get_all_user_consents_endpoint(app):
    client = app.test_client()
    TOKEN = Mock()
    TOKEN.scopes = {}

    with app.test_request_context():
        with patch(
            "perun.utils.consent_framework.consent_manager.ConsentManager"
            ".fetch_all_user_consents",
            return_value=USERS_CONSENTS_IN_DB,
        ), patch(
            "perun.proxygui.user_manager.UserManager" ".sub_to_user_id",
            return_value="existing_user_id",
        ), patch.object(
            consent_api, "current_token", return_value=TOKEN
        ):
            response = client.get("/users/me/consents")

    assert json.loads(response.data) == USERS_CONSENTS_IN_DB
    assert response.status_code == HTTPStatus.OK
