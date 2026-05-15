"""
Account API Test Suite
"""

import os
import logging
from unittest import TestCase
from tests.factories import AccountFactory
from service import talisman
from service.common import status
from service.models import db, Account, init_db
from service.routes import app

BASE_URL = "/accounts"

HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}


class TestAccountService(TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"

        app.logger.setLevel(logging.CRITICAL)

        init_db(app)
        talisman.force_https = False

    def setUp(self):
        db.session.query(Account).delete()
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()

    def _create_accounts(self, count):
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            response = self.client.post(BASE_URL, json=account.serialize())

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            data = response.get_json()
            account.id = data["id"]
            accounts.append(account)

        return accounts

    def test_index(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)

    def test_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["status"], "OK")

    def test_create_account(self):
        account = AccountFactory()

        res = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="application/json"
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(res.headers.get("Location"))

    def test_update_account(self):
        account = self._create_accounts(1)[0]

        res = self.client.put(
            f"{BASE_URL}/{account.id}",
            json={"name": "New Name"}
        )

        self.assertEqual(res.status_code, 200)

    def test_delete_account(self):
        account = self._create_accounts(1)[0]

        res = self.client.delete(f"{BASE_URL}/{account.id}")
        self.assertEqual(res.status_code, 204)

    def test_bad_request(self):
        res = self.client.post(BASE_URL, json={"name": "only"})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        account = AccountFactory()

        res = self.client.post(
            BASE_URL,
            json=account.serialize(),
            content_type="text/html"
        )

        self.assertEqual(
            res.status_code,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
        )
