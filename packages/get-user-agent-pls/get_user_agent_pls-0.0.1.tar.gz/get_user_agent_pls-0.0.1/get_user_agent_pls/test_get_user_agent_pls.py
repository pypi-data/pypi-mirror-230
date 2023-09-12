import os
import unittest
from unittest.mock import patch
from .get_user_agent_pls import fetch_user_agent, USER_AGENTS_FILE

class TestUserAgent(unittest.TestCase):
    def setUp(self):
        self.browser = "chrome"
        self.operating_system = "windows"
        self.file_existed = os.path.exists(USER_AGENTS_FILE)

    def tearDown(self):
        if not self.file_existed and os.path.exists(USER_AGENTS_FILE):
            os.remove(USER_AGENTS_FILE)

    def test_fetch_user_agent(self):
        user_agent = fetch_user_agent(self.browser, self.operating_system)
        self.assertIsNotNone(user_agent)

if __name__ == "__main__":
    unittest.main()
