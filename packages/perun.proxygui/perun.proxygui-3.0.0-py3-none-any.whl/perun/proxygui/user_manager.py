import copy
from typing import Any
from typing import Optional

import sqlalchemy
from perun.connector import AdaptersManager
from perun.connector import Logger
from pymongo.collection import Collection
from sqlalchemy import MetaData
from sqlalchemy import delete, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session

from perun.utils.ConfigStore import ConfigStore
from perun.utils.DatabaseService import DatabaseService
from perun.utils.EmailService import EmailService


class UserManager:
    def __init__(self, cfg):
        GLOBAL_CONFIG = ConfigStore.get_global_cfg(cfg.get("global_cfg_filepath"))
        ADAPTERS_MANAGER_CFG = GLOBAL_CONFIG["adapters_manager"]
        ATTRS_MAP = ConfigStore.get_attributes_map(GLOBAL_CONFIG["attrs_cfg_path"])

        self._ADAPTERS_MANAGER = AdaptersManager(ADAPTERS_MANAGER_CFG, ATTRS_MAP)
        self._SUBJECT_ATTRIBUTE = cfg.get("perun_person_principal_names_attribute")
        self._PREFERRED_MAIL_ATTRIBUTE = cfg["mfa_reset"]["preferred_mail_attribute"]
        self._ALL_MAILS_ATTRIBUTE = cfg["mfa_reset"]["all_mails_attribute"]
        self.email_service = EmailService(cfg)
        self.database_service = DatabaseService(cfg)
        self.logger = Logger.get_logger(__name__)
        self._cfg = cfg

    def extract_user_attribute(self, attr_name: str, user_id: int) -> Any:
        user_attrs = self._ADAPTERS_MANAGER.get_user_attributes(user_id, [attr_name])
        attr_value_candidates = user_attrs.get(attr_name, [])
        attr_value = attr_value_candidates[0] if attr_value_candidates else None

        return attr_value

    def _revoke_ssp_sessions(
        self,
        ssp_sessions_collection: Collection,
        subject: str = None,
        session_id: str = None,
    ) -> int:
        if session_id:
            result = ssp_sessions_collection.delete_many(
                {"sub": subject, "key": session_id}
            )
        elif subject:
            result = ssp_sessions_collection.delete_many({"sub": subject})
        else:
            return 0

        return result.deleted_count

    def _revoke_satosa_grants(
        self,
        satosa_sessions_collection: Collection,
        subject: str = None,
        session_id: str = None,
    ) -> int:
        if session_id:
            result = satosa_sessions_collection.delete_many(
                {"sub": subject, "claims.ssp_session_id": session_id}
            )
        elif subject:
            result = satosa_sessions_collection.delete_many({"sub": subject})
        else:
            return 0

        return result.deleted_count

    def _get_postgres_engine(self) -> Engine:
        connection_string = self._cfg["mitre_database"]["connection_string"]
        engine = sqlalchemy.create_engine(connection_string)

        return engine

    def _get_mitre_delete_statements(
        self,
        engine: Engine,
        user_id: str = None,
        session_id: str = None,
        include_refresh_tokens=False,
    ) -> list[Any]:
        meta_data = MetaData()
        meta_data.reflect(engine)
        session = Session(bind=engine)

        # tables holding general auth data
        AUTH_HOLDER_TBL = meta_data.tables["authentication_holder"]
        SAVED_USER_AUTH_TBL = meta_data.tables["saved_user_auth"]

        matching_username = SAVED_USER_AUTH_TBL.c.name == user_id
        if session_id:
            # if session id is present, we only delete tokens associated with a
            # single specified session
            session_id_attr = (
                self._cfg["mitre_database"]["ssp_session_id_attribute"]
                or "urn:cesnet:proxyidp:attribute:sspSessionID"
            )
            matching_sid = SAVED_USER_AUTH_TBL.c.authentication_attributes.like(
                f'%"{session_id_attr}":["{session_id}"]%'
            )
            user_auth = session.query(SAVED_USER_AUTH_TBL.c.id).filter(
                matching_sid & matching_username
            )
        elif user_id:
            # if only user id is present, we delete all tokens associated
            # with the user
            user_auth = session.query(SAVED_USER_AUTH_TBL.c.id).filter(
                matching_username
            )
        else:
            return []

        # tables holding tokens
        ACCESS_TOKEN_TBL = meta_data.tables["access_token"]
        AUTH_CODE_TBL = meta_data.tables["authorization_code"]
        DEVICE_CODE = meta_data.tables["device_code"]

        token_tables = [ACCESS_TOKEN_TBL, AUTH_CODE_TBL, DEVICE_CODE]

        if include_refresh_tokens:
            REFRESH_TOKEN_TBL = meta_data.tables["refresh_token"]
            token_tables.append(REFRESH_TOKEN_TBL)

        delete_statements = []
        for token_table in token_tables:
            delete_statements.append(
                delete(token_table).where(
                    token_table.c.auth_holder_id.in_(
                        session.query(AUTH_HOLDER_TBL.c.id).filter(
                            AUTH_HOLDER_TBL.c.user_auth_id.in_(user_auth)
                        )
                    )
                )
            )

        return delete_statements

    def _delete_mitre_tokens(
        self,
        user_id: str = None,
        session_id: str = None,
        include_refresh_tokens: bool = False,
    ) -> int:
        deleted_mitre_tokens_count = 0

        engine = self._get_postgres_engine()
        statements = self._get_mitre_delete_statements(
            engine, user_id, session_id, include_refresh_tokens
        )
        with engine.connect() as cnxn:
            for stmt in statements:
                with cnxn.begin():
                    result = cnxn.execute(stmt)
                    deleted_mitre_tokens_count += result.rowcount

        return deleted_mitre_tokens_count

    def _get_satosa_sessions_collection(self) -> Collection:
        return self.database_service.get_mongo_db_collection("satosa_database")

    def _get_ssp_sessions_collection(self) -> Collection:
        return self.database_service.get_mongo_db_collection("ssp_database")

    def sub_to_user_id(self, sub: str, issuer: str) -> Optional[str]:
        """
        Get Perun user ID using user's 'sub' attribute
        :param sub: Perun user's subject attribute
        :return: Perun user ID
        """
        if sub and issuer:
            user = self._ADAPTERS_MANAGER.get_perun_user(idp_id=issuer, uids=[sub])
            if user:
                return str(user.id)

    def logout(
        self,
        user_id: str = None,
        session_id: str = None,
        include_refresh_tokens: bool = False,
    ) -> None:
        """
        Performs revocation of user's sessions based on the provided user_id or
        session_id. If none are provided, revocation is not performed. If
        both are
        provided, only a single session is revoked if it exists. If only
        user id is
        provided, all of user's sessions are revoked.
        :param user_id: id of user whose sessions are to be revoked
        :param session_id: id of a specific session to revoke
        :param include_refresh_tokens: specifies whether refresh tokens
        should be
        canceled as well
        :return: Nothing
        """
        if not user_id:
            self.logger.info(
                "No user id provided. Please, provide at least user id to "
                "perform "
                "logout."
            )
            return
        subject = self.extract_user_attribute(self._SUBJECT_ATTRIBUTE, int(user_id))

        satosa_sessions_collection = self._get_satosa_sessions_collection()
        revoked_grants_count = self._revoke_satosa_grants(
            satosa_sessions_collection, subject, session_id
        )

        deleted_tokens_count = self._delete_mitre_tokens(
            user_id=user_id, include_refresh_tokens=include_refresh_tokens
        )

        ssp_sessions_collection = self._get_ssp_sessions_collection()
        revoked_sessions_count = self._revoke_ssp_sessions(
            ssp_sessions_collection, subject, session_id
        )

        self.logger.info(
            f"Logged out user {subject} from {revoked_sessions_count} SSP "
            f"sessions, deleted {revoked_grants_count} SATOSA sessions and "
            f"deleted {deleted_tokens_count} mitre tokens."
        )

    def get_active_client_ids_for_user(self, user_id: str) -> set[str]:
        """
        Returns list of unique client ids retrieved from active user's
        sessions.
        :param user_id: user, whose sessions are retrieved
        :return: list of client ids
        """
        subject = self.extract_user_attribute(self._SUBJECT_ATTRIBUTE, int(user_id))

        ssp_clients = self._get_ssp_entity_ids_by_user(subject)
        satosa_clients = self._get_satosa_client_ids(subject)
        mitre_clients = self._get_mitre_client_ids(user_id)

        return set(ssp_clients + satosa_clients + mitre_clients)

    def _get_mitre_client_ids(self, user_id: str) -> list[str]:
        engine = self._get_postgres_engine()
        meta_data = MetaData()
        meta_data.reflect(engine)
        session = Session(bind=engine)

        AUTH_HOLDER_TBL = meta_data.tables["authentication_holder"]
        SAVED_USER_AUTH_TBL = meta_data.tables["saved_user_auth"]
        ACCESS_TOKEN_TBL = meta_data.tables["access_token"]
        CLIENT_DETAILS_TBL = meta_data.tables["client_details"]

        with engine.connect() as cnxn:
            with cnxn.begin():
                stmt = select(CLIENT_DETAILS_TBL.c.client_id).where(
                    CLIENT_DETAILS_TBL.c.id.in_(
                        session.query(ACCESS_TOKEN_TBL.c.client_id).filter(
                            ACCESS_TOKEN_TBL.c.auth_holder_id.in_(
                                session.query(AUTH_HOLDER_TBL.c.id).filter(
                                    AUTH_HOLDER_TBL.c.user_auth_id.in_(
                                        session.query(SAVED_USER_AUTH_TBL.c.id).filter(
                                            SAVED_USER_AUTH_TBL.c.name == user_id
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
                result = cnxn.execute(stmt)
        return [r[0] for r in result]

    def _get_ssp_entity_ids_by_user(self, sub: str):
        ssp_sessions_collection = self._get_ssp_sessions_collection()
        entries = ssp_sessions_collection.find(
            {"user": sub}, {"entityIds": 1, "_id": 0}
        )
        entries = [entry.get("entityIds", []) for entry in entries]
        return [el for lst in entries for el in lst]

    def _get_ssp_entity_ids_by_session(self, session_id: str):
        ssp_sessions_collection = self._get_ssp_sessions_collection()
        entries = ssp_sessions_collection.find(
            {"key": session_id}, {"entityIds": 1, "_id": 0}
        )
        entries = [entry.get("entityIds", []) for entry in entries]
        return [el for lst in entries for el in lst]

    def _get_satosa_client_ids(self, sub: str):
        satosa_sessions_collection = self._get_satosa_sessions_collection()
        result = satosa_sessions_collection.find(
            {"sub": sub}, {"client_id": 1, "_id": 0}
        )
        return list(result)

    def handle_mfa_reset(
        self, user_id: str, locale: str, mfa_reset_verify_url: str
    ) -> str:
        # send MFA reset confirmation link
        preferred_mail = self.extract_user_attribute(
            self._PREFERRED_MAIL_ATTRIBUTE, int(user_id)
        )
        self.email_service.send_mfa_reset_link(
            preferred_mail, locale, mfa_reset_verify_url
        )

        # send notification about MFA reset
        if self._ALL_MAILS_ATTRIBUTE:
            all_user_mails = self.extract_user_attribute(
                self._ALL_MAILS_ATTRIBUTE, int(user_id)
            )
            non_preferred_mails = copy.deepcopy(all_user_mails)
            if preferred_mail in all_user_mails:
                non_preferred_mails.remove(preferred_mail)
            self.email_service.send_mfa_reset_notification(non_preferred_mails, locale)

        return preferred_mail

    def forward_mfa_reset_request(self, requester_email: str) -> None:
        self.email_service.send_mfa_reset_request(requester_email)
