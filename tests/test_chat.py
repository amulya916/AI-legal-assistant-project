import unittest
from flask import Flask, session
from werkzeug.security import generate_password_hash
import sys
import os

# Include project root in python search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models.database import execute_db, query_db

class TestChat(unittest.TestCase):
    """Integration tests for the AI Chatbot routes, messaging, and history clearing."""
    
    def setUp(self):
        # Build app instance for testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.db_path = 'test_chat_database.db'
        self.app.config['DATABASE_PATH'] = self.db_path
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Re-initialize test database tables
        from models.database import init_db
        init_db()
        
        # Pre-seed a test user
        hashed_password = generate_password_hash('password123')
        self.user_id = execute_db(
            "INSERT INTO Users (name, email, password) VALUES (?, ?, ?)",
            ('Test User', 'testuser@test.com', hashed_password)
        )
        
        # Log in the user by setting the session variables
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user_id
            sess['name'] = 'Test User'
            sess['email'] = 'testuser@test.com'
            sess['role'] = 'user'
            
    def tearDown(self):
        self.app_context.pop()
        # Clean up database file
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except PermissionError:
                pass
                
    def test_chatbot_index(self):
        """Test that the main chatbot page renders and shows history."""
        # Insert a chat record first
        execute_db(
            "INSERT INTO Chats (user_id, message, response) VALUES (?, ?, ?)",
            (self.user_id, 'Hello', 'Hi there, how can I help you?')
        )
        
        response = self.client.get('/chatbot')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello', response.data)
        self.assertIn(b'Hi there, how can I help you?', response.data)
        
    def test_chatbot_send_message(self):
        """Test sending a message to the chatbot endpoint (which runs in mock/simulator mode during testing)."""
        response = self.client.post('/chatbot/send', json={
            'message': 'What are consumer rights?'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('response', data)
        self.assertEqual(data['message'], 'What are consumer rights?')
        
        # Check database entry was created
        chat = query_db("SELECT * FROM Chats WHERE user_id = ?", (self.user_id,), one=True)
        self.assertIsNotNone(chat)
        self.assertEqual(chat['message'], 'What are consumer rights?')
        
    def test_clear_conversation(self):
        """Test the new clear conversation route deletes all chat history for the user."""
        # Insert multiple chat records
        execute_db(
            "INSERT INTO Chats (user_id, message, response) VALUES (?, ?, ?)",
            (self.user_id, 'Question 1', 'Answer 1')
        )
        execute_db(
            "INSERT INTO Chats (user_id, message, response) VALUES (?, ?, ?)",
            (self.user_id, 'Question 2', 'Answer 2')
        )
        
        # Verify chats exist
        chats_before = query_db("SELECT COUNT(*) as count FROM Chats WHERE user_id = ?", (self.user_id,), one=True)['count']
        self.assertEqual(chats_before, 2)
        
        # Hit clear route
        response = self.client.get('/chatbot/clear', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Started a new conversation', response.data)
        
        # Verify chats are deleted
        chats_after = query_db("SELECT COUNT(*) as count FROM Chats WHERE user_id = ?", (self.user_id,), one=True)['count']
        self.assertEqual(chats_after, 0)

if __name__ == '__main__':
    unittest.main()
