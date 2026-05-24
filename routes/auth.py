from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import execute_db, query_db
from utils.validators import is_valid_email, is_strong_password
from utils.helpers import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user account."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validations
        if not name or not email or not password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('register.html', name=name, email=email)
            
        if not is_valid_email(email):
            flash('Invalid email address format.', 'danger')
            return render_template('register.html', name=name, email=email)
            
        if not is_strong_password(password):
            flash('Password must be at least 6 characters long and contain both letters and numbers.', 'danger')
            return render_template('register.html', name=name, email=email)
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', name=name, email=email)
            
        # Check if email exists
        user = query_db("SELECT id FROM Users WHERE email = ?", (email,), one=True)
        if user:
            flash('Email address is already registered.', 'danger')
            return render_template('register.html', name=name, email=email)
            
        # Hash password and save
        hashed_password = generate_password_hash(password)
        try:
            user_id = execute_db(
                "INSERT INTO Users (name, email, password, role) VALUES (?, ?, ?, ?)",
                (name, email, hashed_password, 'user')
            )
            # Log in automatically
            session['user_id'] = user_id
            session['name'] = name
            session['email'] = email
            session['role'] = 'user'
            flash('Registration successful! Welcome to AI Legal Assistant.', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'danger')
            
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate user credentials."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html', email=email)
            
        user = query_db("SELECT * FROM Users WHERE email = ?", (email,), one=True)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid email or password.', 'danger')
            return render_template('login.html', email=email)
            
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    """Clear session data and redirect to homepage."""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle password reset requests with a visual confirmation simulation."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not email or not new_password or not confirm_password:
            flash('All fields are required.', 'danger')
            return render_template('forgot_password.html', email=email)
            
        user = query_db("SELECT id FROM Users WHERE email = ?", (email,), one=True)
        if not user:
            flash('No account found with that email address.', 'danger')
            return render_template('forgot_password.html', email=email)
            
        if not is_strong_password(new_password):
            flash('Password must be at least 6 characters long and contain both letters and numbers.', 'danger')
            return render_template('forgot_password.html', email=email)
            
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('forgot_password.html', email=email)
            
        # Update user's password
        hashed_password = generate_password_hash(new_password)
        execute_db("UPDATE Users SET password = ? WHERE email = ?", (hashed_password, email))
        flash('Your password has been reset successfully. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('forgot_password.html')

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Allow logged in user to modify password from profile."""
    current_password = request.form.get('current_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not current_password or not new_password or not confirm_password:
        flash('All fields are required.', 'danger')
        return redirect(url_for('dashboard.profile'))
        
    user = query_db("SELECT password FROM Users WHERE id = ?", (session['user_id'],), one=True)
    
    if not user or not check_password_hash(user['password'], current_password):
        flash('Incorrect current password.', 'danger')
        return redirect(url_for('dashboard.profile'))
        
    if not is_strong_password(new_password):
        flash('New password must be at least 6 characters long and contain both letters and numbers.', 'danger')
        return redirect(url_for('dashboard.profile'))
        
    if new_password != confirm_password:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('dashboard.profile'))
        
    hashed_password = generate_password_hash(new_password)
    execute_db("UPDATE Users SET password = ? WHERE id = ?", (hashed_password, session['user_id']))
    flash('Password changed successfully.', 'success')
    return redirect(url_for('dashboard.profile'))
