"""Check database guards without importing the app or touching a database."""
import os
import runpy
import unittest
from pathlib import Path
from unittest.mock import patch

prepare = runpy.run_path(str(Path(__file__).with_name("live_llm_paid_path_demo.py")))["_prepare_env"]

class DemoDatabaseGuardTests(unittest.TestCase):
    def test_local_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(prepare()["TEST_DATABASE_URL"].endswith("/ancap_investor_demo_20261014"))

    def test_local_named_database(self):
        url = "postgresql+asyncpg://test:test@127.0.0.1:5432/ancap_investor_demo_20261014_check"
        with patch.dict(os.environ, {"TEST_DATABASE_URL": url}, clear=True):
            self.assertEqual(prepare()["DATABASE_URL"], url)

    def test_database_name_cannot_be_hidden_in_username(self):
        with patch.dict(os.environ, {"TEST_DATABASE_URL": "postgresql://ancap_investor_demo:secret@localhost/ancap"}, clear=True):
            with self.assertRaises(SystemExit):
                prepare()

    def test_remote_host_rejected(self):
        with patch.dict(os.environ, {"TEST_DATABASE_URL": "postgresql://test:secret@example.com/ancap_investor_demo_20261014"}, clear=True):
            with self.assertRaises(SystemExit):
                prepare()

    def test_override_cannot_disable_guard(self):
        with patch.dict(os.environ, {"TEST_DATABASE_URL": "postgresql://test:secret@localhost/ancap", "ALLOW_NON_DEMO_DB": "1"}, clear=True):
            with self.assertRaises(SystemExit):
                prepare()

    def test_error_does_not_expose_url(self):
        with patch.dict(os.environ, {"TEST_DATABASE_URL": "invalid-secret-url"}, clear=True):
            with self.assertRaises(SystemExit) as error:
                prepare()
            self.assertNotIn("invalid-secret-url", str(error.exception))

if __name__ == "__main__":
    unittest.main()
