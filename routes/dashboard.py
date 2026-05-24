from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from models.database import query_db, execute_db
from utils.helpers import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Render user dashboard with usage statistics and logs."""
    user_id = session['user_id']
    
    # 1. Fetch counts
    chat_count = query_db("SELECT COUNT(*) as count FROM Chats WHERE user_id = ?", (user_id,), one=True)['count']
    saved_count = query_db("SELECT COUNT(*) as count FROM Chats WHERE user_id = ? AND saved = 1", (user_id,), one=True)['count']
    notice_count = query_db("SELECT COUNT(*) as count FROM Legal_Notices WHERE user_id = ?", (user_id,), one=True)['count']
    document_count = query_db("SELECT COUNT(*) as count FROM Uploaded_Documents WHERE user_id = ?", (user_id,), one=True)['count']
    
    # 2. Fetch lists
    recent_chats = query_db(
        "SELECT * FROM Chats WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5",
        (user_id,)
    )
    saved_chats = query_db(
        "SELECT * FROM Chats WHERE user_id = ? AND saved = 1 ORDER BY timestamp DESC LIMIT 10",
        (user_id,)
    )
    recent_notices = query_db(
        "SELECT * FROM Legal_Notices WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (user_id,)
    )
    
    # 3. User details
    user = query_db("SELECT * FROM Users WHERE id = ?", (user_id,), one=True)
    
    return render_template(
        'dashboard.html',
        chat_count=chat_count,
        saved_count=saved_count,
        notice_count=notice_count,
        document_count=document_count,
        recent_chats=recent_chats,
        saved_chats=saved_chats,
        recent_notices=recent_notices,
        user=user
    )

@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Render and update user profile settings."""
    user_id = session['user_id']
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        
        if not name or not email:
            flash('Name and email are required.', 'danger')
            return redirect(url_for('dashboard.profile'))
            
        # Check if email is already taken by someone else
        existing = query_db("SELECT id FROM Users WHERE email = ? AND id != ?", (email, user_id), one=True)
        if existing:
            flash('This email address is already taken by another account.', 'danger')
            return redirect(url_for('dashboard.profile'))
            
        execute_db("UPDATE Users SET name = ?, email = ? WHERE id = ?", (name, email, user_id))
        session['name'] = name
        session['email'] = email
        flash('Profile settings updated successfully.', 'success')
        return redirect(url_for('dashboard.profile'))
        
    user = query_db("SELECT * FROM Users WHERE id = ?", (user_id,), one=True)
    return render_template('profile.html', user=user)
