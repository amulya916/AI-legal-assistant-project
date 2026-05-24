from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from models.database import query_db, execute_db
from utils.helpers import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@admin_required
def index():
    """Render admin control center with site statistics, user tables, and feedback logs."""
    # 1. Base Statistics
    stats = {}
    stats['total_users'] = query_db("SELECT COUNT(*) as count FROM Users", one=True)['count']
    stats['total_chats'] = query_db("SELECT COUNT(*) as count FROM Chats", one=True)['count']
    stats['total_notices'] = query_db("SELECT COUNT(*) as count FROM Legal_Notices", one=True)['count']
    stats['total_documents'] = query_db("SELECT COUNT(*) as count FROM Uploaded_Documents", one=True)['count']
    stats['total_feedback'] = query_db("SELECT COUNT(*) as count FROM Feedback", one=True)['count']
    
    avg_rating_row = query_db("SELECT AVG(rating) as avg_rating FROM Feedback", one=True)
    stats['avg_rating'] = round(avg_rating_row['avg_rating'], 2) if avg_rating_row['avg_rating'] else 0.0
    
    # 2. Fetch all users
    users = query_db("SELECT id, name, email, role, created_at FROM Users ORDER BY created_at DESC")
    
    # 3. Chat usage per user
    user_usage = query_db("""
        SELECT Users.id, Users.name, Users.email, COUNT(Chats.id) as chat_count
        FROM Users
        LEFT JOIN Chats ON Users.id = Chats.user_id
        GROUP BY Users.id
        ORDER BY chat_count DESC
    """)
    
    # 4. Fetch all feedback logs
    feedback_logs = query_db("""
        SELECT Feedback.id, Users.name as user_name, Users.email, Feedback.rating, Feedback.feedback, Feedback.created_at
        FROM Feedback
        JOIN Users ON Feedback.user_id = Users.id
        ORDER BY Feedback.created_at DESC
    """)
    
    return render_template(
        'admin.html',
        stats=stats,
        users=users,
        user_usage=user_usage,
        feedback_logs=feedback_logs
    )

@admin_bp.route('/admin/user/role/<int:user_id>', methods=['POST'])
@admin_required
def change_role(user_id):
    """Toggle a user's role between user and admin."""
    new_role = request.form.get('role')
    
    if new_role not in ['user', 'admin']:
        flash('Invalid role specified.', 'danger')
        return redirect(url_for('admin.index'))
        
    # Prevent self-demotion
    if user_id == session['user_id']:
        flash('You cannot change your own administrative role.', 'warning')
        return redirect(url_for('admin.index'))
        
    execute_db("UPDATE Users SET role = ? WHERE id = ?", (new_role, user_id))
    flash('User role updated successfully.', 'success')
    return redirect(url_for('admin.index'))

@admin_bp.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user account entirely."""
    # Prevent self-deletion
    if user_id == session['user_id']:
        flash('You cannot delete your own active administrative account.', 'warning')
        return redirect(url_for('admin.index'))
        
    execute_db("DELETE FROM Users WHERE id = ?", (user_id,))
    flash('User account deleted successfully.', 'success')
    return redirect(url_for('admin.index'))
