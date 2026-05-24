import sqlite3
from flask import current_app
from werkzeug.security import generate_password_hash
import os

def get_db_connection():
    """Establish a connection to the SQLite database with Row Factory configured."""
    db_path = current_app.config['DATABASE_PATH']
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initialize the SQLite tables based on the database schema and seed default data."""
    db_path = current_app.config['DATABASE_PATH']
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Create Users Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 2. Create Chats Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        response TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        saved INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
    )
    ''')
    
    # 3. Create Feedback Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        feedback TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
    )
    ''')
    
    # 4. Create Legal_Notices Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Legal_Notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        notice_type TEXT NOT NULL,
        generated_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
    )
    ''')
    
    # 5. Create Uploaded_Documents Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Uploaded_Documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        file_name TEXT NOT NULL,
        summary TEXT,
        key_points TEXT,
        simplified TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    
    # Seed default admin if it doesn't exist
    cursor.execute("SELECT id FROM Users WHERE email = ?", ('admin@legalassistant.com',))
    admin_exists = cursor.fetchone()
    
    if not admin_exists:
        hashed_password = generate_password_hash('adminpassword')
        cursor.execute(
            "INSERT INTO Users (name, email, password, role) VALUES (?, ?, ?, ?)",
            ('System Admin', 'admin@legalassistant.com', hashed_password, 'admin')
        )
        conn.commit()
        
    conn.close()

def query_db(query, args=(), one=False):
    """Convenience method to query the database and fetch rows."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """Convenience method to execute insert/update/delete operations."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    lastrowid = cur.lastrowid
    conn.close()
    return lastrowid
