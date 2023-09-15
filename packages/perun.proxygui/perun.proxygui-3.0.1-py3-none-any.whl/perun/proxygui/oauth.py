from http import HTTPStatus
from typing import Dict, Optional

import requests
import validators
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.oauth2.rfc6750 import InvalidTokenError, InsufficientScopeError
from authlib.oauth2.rfc7662 import IntrospectTokenValidator
from perun.connector import Logger


class MyIntrospectTokenValidator(IntrospectTokenValidator):
    def __init__(self, **extra_attributes):
        super().__init__(**extra_attributes)
        self.client_id = None
        self.client_secret = None
        self.introspect_url = None

    def introspect_token(self, token_string):
        url = self.introspect_url
        data = {"token": token_string, "token_type_hint": "access_token"}
        auth = (self.client_id, self.client_secret)
        response = requests.post(url, data=data, auth=auth)
        response.raise_for_status()

        return response.json()

    def validate_token(self, token, scopes, request):
        if not token or not token.get("active"):
            raise InvalidTokenError(
                realm=self.realm, extra_attributes=self.extra_attributes
            )
        if token.is_expired() or token.is_revoked():
            raise InvalidTokenError()
        if self.scope_insufficient(token.get_scope(), scopes):
            raise InsufficientScopeError()

        return token


require_oauth = ResourceProtector()
my_validator = MyIntrospectTokenValidator()
require_oauth.register_token_validator(my_validator)
logger = Logger.get_logger(__name__)


def get_introspect_url(issuer: str) -> Optional[str]:
    metadata_endpoint = f"{issuer}.well-known/openid-configuration'"
    if not validators.url(metadata_endpoint):
        return None

    response = requests.get(metadata_endpoint)

    if response.status_code != HTTPStatus.OK:
        logger.info(
            f"Introspection url could not be obtained. Metadata endpoint '"
            f"{metadata_endpoint}' responded with '{response.status_code} - "
            f"{response.json()}'"
        )
        return None

    metadata = response.json()
    return metadata.get("introspection_endpoint")


def configure_resource_protector(oauth_cfg: Dict[str, str]) -> None:
    validator = require_oauth.get_token_validator(my_validator.TOKEN_TYPE)

    validator.client_id = (oauth_cfg["client_id"],)
    validator.client_secret = (oauth_cfg["client_secret"],)
    validator.introspect_url = get_introspect_url(oauth_cfg["issuer"])
