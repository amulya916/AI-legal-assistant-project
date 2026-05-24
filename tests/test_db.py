import unittest
from flask import Flask
import sys
import os

# Include project root in python search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.database import init_db, query_db, execute_db

class TestDatabase(unittest.TestCase):
    """Unit tests for SQLite database schemas, initialization, and CRUD operations."""
    
    def setUp(self):
        self.app = Flask(__name__)
        # Use file-based DB for testing since :memory: wrings tables when connection is closed
        self.db_path = 'test_database.db'
        self.app.config['DATABASE_PATH'] = self.db_path
        self.app_context = self.app.app_context()
        self.app_context.push()
        init_db()
        
    def tearDown(self):
        self.app_context.pop()
        # Clean up database file
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass
        
    def test_admin_user_seeding(self):
        """Verify that default admin accounts are seeded on creation."""
        admin = query_db("SELECT * FROM Users WHERE email = ?", ('admin@legalassistant.com',), one=True)
        self.assertIsNotNone(admin)
        self.assertEqual(admin['role'], 'admin')
        self.assertEqual(admin['name'], 'System Admin')
        
    def test_crud_user_lifecycle(self):
        """Test full insert, select, update, and delete lifecycle on SQLite tables."""
        # 1. Create (Insert)
        user_id = execute_db(
            "INSERT INTO Users (name, email, password) VALUES (?, ?, ?)",
            ("Test User", "test@test.com", "hashedpassword")
        )
        self.assertIsNotNone(user_id)
        
        # 2. Read (Query)
        user = query_db("SELECT * FROM Users WHERE id = ?", (user_id,), one=True)
        self.assertEqual(user['name'], "Test User")
        self.assertEqual(user['email'], "test@test.com")
        self.assertEqual(user['role'], "user") # Default value check
        
        # 3. Update (Execute)
        execute_db("UPDATE Users SET role = ? WHERE id = ?", ("admin", user_id))
        user_updated = query_db("SELECT * FROM Users WHERE id = ?", (user_id,), one=True)
        self.assertEqual(user_updated['role'], "admin")
        
        # 4. Delete (Execute)
        execute_db("DELETE FROM Users WHERE id = ?", (user_id,))
        user_deleted = query_db("SELECT * FROM Users WHERE id = ?", (user_id,), one=True)
        self.assertIsNone(user_deleted)

if __name__ == '__main__':
    unittest.main()
