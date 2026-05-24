import unittest
from flask import Flask, session
from werkzeug.security import generate_password_hash
import sys
import os

# Include project root in python search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models.database import execute_db, query_db

class TestAuth(unittest.TestCase):
    """Integration and unit tests for authentication routes and credential checking."""
    
    def setUp(self):
        # Build app instance for testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.db_path = 'test_auth_database.db'
        self.app.config['DATABASE_PATH'] = self.db_path
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Re-initialize in-memory tables
        from models.database import init_db
        init_db()
        
    def tearDown(self):
        self.app_context.pop()
        # Clean up database file
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass
        
    def test_user_registration(self):
        """Test registration endpoint with valid parameters and verify database insertion."""
        response = self.client.post('/register', data={
            'name': 'Alice Smith',
            'email': 'alice@test.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check database entry
        user = query_db("SELECT * FROM Users WHERE email = ?", ('alice@test.com',), one=True)
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], 'Alice Smith')
        
    def test_user_login_success(self):
        """Test login endpoint using registered credentials."""
        # Pre-populate user record
        hashed_password = generate_password_hash('password123')
        execute_db(
            "INSERT INTO Users (name, email, password) VALUES (?, ?, ?)",
            ('Bob Jones', 'bob@test.com', hashed_password)
        )
        
        # Call login endpoint
        response = self.client.post('/login', data={
            'email': 'bob@test.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
    def test_user_login_failures(self):
        """Test login failures with incorrect passwords."""
        hashed_password = generate_password_hash('password123')
        execute_db(
            "INSERT INTO Users (name, email, password) VALUES (?, ?, ?)",
            ('Bob Jones', 'bob@test.com', hashed_password)
        )
        
        # Submit wrong credentials
        response = self.client.post('/login', data={
            'email': 'bob@test.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        # Verify page shows failure flashes
        self.assertIn(b'Invalid email or password', response.data)

if __name__ == '__main__':
    unittest.main()
