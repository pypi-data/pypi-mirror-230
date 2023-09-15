import datetime
import json
import secrets

from authlib.jose import jwt
from jwcrypto import jwk
from jwcrypto.jwk import JWKSet, JWK
from typing_extensions import Dict, Any

from perun.utils.DatabaseService import DatabaseService


class JWTService:
    def __init__(self, cfg):
        self.__KEYSTORE = cfg.get("keystore")
        self.__KEY_ID = cfg.get("key_id")
        self.__JWK_SET = None
        self.__DATABASE_SERVICE = DatabaseService(cfg)

    def __import_keys(self) -> JWKSet:
        jwk_set = jwk.JWKSet()
        with open(self.__KEYSTORE, "r") as file:
            jwk_set.import_keyset(file.read())
        return jwk_set

    def __get_signing_jwk(self) -> JWK:
        jwk_set = self.__JWK_SET if self.__JWK_SET else self.__import_keys()

        return jwk_set.get_key(self.__KEY_ID)

    def verify_jwt(self, token) -> Dict[Any, Any]:
        """
        Verifies that the JWT is valid - it is not expired and hasn't been
        used yet.

        :param token: JWT to verify
        :return: content of the JWT if it's valid, empty dict otherwise
        """
        jwk_key = self.__get_signing_jwk()
        claims = jwt.JWT(jwt=token, key=jwk_key).claims
        message = json.loads(claims)

        # verify that the token is not expired
        expiration_date = message.get("exp")
        if datetime.datetime.now() >= expiration_date:
            return {}

        # verify that the token hasn't been used yet
        nonce = message.get("nonce")
        jwt_nonce_collection = self.__DATABASE_SERVICE.get_mongo_db_collection(
            "jwt_nonce_database"
        )
        is_used_nonce = (
            jwt_nonce_collection.count_documents({"used_nonce": nonce}, limit=1) > 0
        )
        if is_used_nonce:
            return {}

        jwt_nonce_collection.insert_one({"used_nonce": nonce})

        return message

    def get_jwt(self, token_args: Dict[str, Any], lifetime_hours: int = 24) -> bytes:
        """
        Constructs a signed JWT containing expiration time and nonce by
        default. Other attributes to be added can be passed in token_args.

        :param token_args: dict of attributes to be added to the signed JWT
        :param lifetime_hours: How long should the token stay valid
        :return: signed and encoded JWT
        """
        token_info = {
            "nonce": secrets.token_urlsafe(16),
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(hours=lifetime_hours),
        }

        if token_args:
            token_info.update(token_args)
        signing_key = self.__get_signing_jwk()
        encoded_token = jwt.encode(payload=token_info, key=signing_key)

        return encoded_token
