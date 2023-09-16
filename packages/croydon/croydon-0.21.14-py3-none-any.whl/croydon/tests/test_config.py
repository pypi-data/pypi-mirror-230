from unittest import TestCase
from croydon.config import BaseConfig


class TestConfig(TestCase):

    def test_config(self):
        cfg = BaseConfig()
        self.assertEqual(cfg.get("session.cookie"), cfg.session.cookie)
        with self.assertRaises(KeyError):
            cfg.get("some.incorrect.key")
