from datetime import datetime
from unittest import TestCase

import mongomock

from perun.utils.consent_framework.consent import Consent
from perun.utils.consent_framework.consent_db import ConsentDB


class TestConsentDB(TestCase):
    def setUp(self):
        self.cfg = {
            "consent": {"months_valid": 6},
            "test_db": {
                "connection_string": "mongodb://localhost:27017/",
                "database_name": "test_db",
                "consent_collection_name": "test_collection",
            },
        }
        self.mock_client = mongomock.MongoClient()
        self.mock_collection = self.mock_client.test_db.test_collection
        self.consent_db = ConsentDB(self.cfg, "test_db")
        self.consent1 = Consent(
            {"test_attribute": "test_value"},
            "test_user_id1",
            "test_requester",
            6,
            datetime.utcnow(),
        )
        self.consent2 = Consent(
            {"test_attribute": "test_value"},
            "test_user_id2",
            "test_requester",
            6,
            datetime.utcnow(),
        )

    def test_save_consent(self):
        self.consent_db.collection = self.mock_collection
        self.consent_db.save_consent("test_consent_id", self.consent1)
        self.assertTrue(
            self.mock_collection.find_one({"consent_id": "test_consent_id"})
        )

    def test_get_consent(self):
        self.consent_db.collection = self.mock_collection
        self.consent_db.save_consent("test_consent_id", self.consent1)
        result = self.consent_db.get_consent("test_consent_id")
        self.assertEqual(result.attributes, {"test_attribute": "test_value"})
        self.assertEqual(result.user_id, "test_user_id1")
        self.assertEqual(result.requester, "test_requester")
        self.assertEqual(result.months_valid, 6)

    def test_delete_consent(self):
        self.consent_db.collection = self.mock_collection
        self.consent_db.save_consent("test_consent_id", self.consent1)
        self.consent_db.delete_consent("test_consent_id")
        self.assertIsNone(
            self.mock_collection.find_one({"consent_id": "test_consent_id"})
        )

    def test_delete_all_user_consents(self):
        self.consent_db.collection = self.mock_collection
        self.consent_db.save_consent("test_consent_id1", self.consent1)
        self.consent_db.save_consent("test_consent_id2", self.consent1)
        self.consent_db.delete_all_user_consents("test_user_id1")
        self.assertEqual(
            self.mock_collection.count_documents({"user_id": "test_user_id1"}), 0
        )

    def test_delete_single_user_consent_consent_exists(self):
        self.consent_db.collection = self.mock_collection
        self.consent_db.save_consent("test_consent_id1", self.consent1)
        self.consent_db.save_consent("test_consent_id2", self.consent1)

        self.assertEqual(
            self.mock_collection.count_documents({"user_id": "test_user_id1"}), 2
        )

        deleted_count = self.consent_db.delete_user_consent("test_consent_id2")

        self.assertEqual(deleted_count, 1)
        self.assertEqual(
            self.mock_collection.count_documents({"user_id": "test_user_id1"}), 1
        )
        self.assertEqual(
            self.mock_collection.count_documents({"consent_id": "test_consent_id1"}), 1
        )
        self.assertEqual(
            self.mock_collection.count_documents({"consent_id": "test_consent_id2"}), 0
        )

    def test_delete_single_user_consent_consent_doesnt_exist(self):
        self.consent_db.collection = self.mock_collection
        self.consent_db.save_consent("test_consent_id1", self.consent1)

        self.assertEqual(
            self.mock_collection.count_documents({"user_id": "test_user_id1"}), 1
        )

        deleted_count = self.consent_db.delete_user_consent("test_consent_fake_id")

        self.assertEqual(deleted_count, 0)
        self.assertEqual(
            self.mock_collection.count_documents({"user_id": "test_user_id1"}), 1
        )

    def test_get_all_user_consents(self):
        self.consent_db.collection = self.mock_collection
        # consent1 and consent2 belong to differnet users
        self.consent_db.save_consent("test_consent_id1", self.consent1)
        self.consent_db.save_consent("test_consent_id2", self.consent1)
        self.consent_db.save_consent("test_consent_id3", self.consent2)

        obtained_consents = self.consent_db.get_all_user_consents("test_user_id1")
        self.assertEqual(len(obtained_consents), 2)

        obtained_consents = self.consent_db.get_all_user_consents("test_user_id2")
        self.assertEqual(len(obtained_consents), 1)
