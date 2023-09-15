import unittest
from unittest.mock import patch
from io import StringIO
from cli import auth_app


class TestAuthApp(unittest.TestCase):

    def test_auth_status(self):
        with patch('sys.stdout', new=StringIO()) as mock_output:
            auth_app(['status'])
            self.assertIn('Print whether logged in or not', mock_output.getvalue())

    def test_login(self):
        with patch('sys.stdout', new=StringIO()) as mock_output:
            auth_app(['login', '--token', 'test-token'])
            self.assertIn('Logging using the authorization token: test-token', mock_output.getvalue())

    def test_logout(self):
        with patch('sys.stdout', new=StringIO()) as mock_output:
            auth_app(['logout'])
            self.assertIn('Logging out of current session', mock_output.getvalue())

if __name__ == '__main__':
    unittest.main()
