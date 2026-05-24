import unittest
import sys
import os

# Include project root in python search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.validators import is_valid_email, is_strong_password

class TestValidators(unittest.TestCase):
    """Unit tests for the validator functions in utils/validators.py."""
    
    def test_valid_emails(self):
        self.assertTrue(is_valid_email("test@example.com"))
        self.assertTrue(is_valid_email("user.name+tag@sub.domain.co.in"))
        self.assertTrue(is_valid_email("admin_123@legal-assistant.org"))
        
    def test_invalid_emails(self):
        self.assertFalse(is_valid_email("invalid-email"))
        self.assertFalse(is_valid_email("test@example"))
        self.assertFalse(is_valid_email("@domain.com"))
        self.assertFalse(is_valid_email("test@.com"))
        
    def test_strong_passwords(self):
        self.assertTrue(is_strong_password("Pass123"))
        self.assertTrue(is_strong_password("a1b2c3d4"))
        self.assertTrue(is_strong_password("Secure99!"))
        
    def test_weak_passwords(self):
        # Too short
        self.assertFalse(is_strong_password("a1"))
        # Letters only
        self.assertFalse(is_strong_password("password"))
        # Digits only
        self.assertFalse(is_strong_password("12345678"))

if __name__ == '__main__':
    unittest.main()
