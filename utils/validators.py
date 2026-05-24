import re
from flask import current_app

def is_valid_email(email):
    """Validate email structure using regular expression."""
    pattern = r'^[\w\.\+-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    """Validate password strength (must be at least 6 characters, contain letters and numbers)."""
    if len(password) < 6:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    return True

def allowed_file(filename):
    """Validate uploaded document extensions based on application config."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
