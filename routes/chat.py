from flask import Blueprint, render_template, request, jsonify, session, send_file, flash, redirect, url_for
from models.database import execute_db, query_db
from utils.helpers import login_required
from services import gemini_service, pdf_service
import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chatbot')
@login_required
def index():
    """Render the main chatbot page and load history."""
    user_id = session['user_id']
    # Load recent 50 chat records
    chats = query_db(
        "SELECT * FROM Chats WHERE user_id = ? ORDER BY timestamp ASC LIMIT 50",
        (user_id,)
    )
    return render_template('chatbot.html', chats=chats)

@chat_bp.route('/chatbot/send', methods=['POST'])
@login_required
def send_message():
    """Receive user message, query Gemini, save both, and return response."""
    user_id = session['user_id']
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'error': 'Message content is missing.'}), 400
        
    message = data['message'].strip()
    if not message:
        return jsonify({'error': 'Message cannot be empty.'}), 400
        
    # Get previous context
    history_rows = query_db(
        "SELECT message, response FROM Chats WHERE user_id = ? ORDER BY timestamp DESC LIMIT 6",
        (user_id,)
    )
    
    # Reverse to keep chronological order
    chat_history = []
    for row in reversed(history_rows):
        chat_history.append({'message': row['message'], 'response': row['response']})
        
    # Call Gemini service
    response_text = gemini_service.generate_chat_response(message, chat_history)
    
    # Save to database
    chat_id = execute_db(
        "INSERT INTO Chats (user_id, message, response) VALUES (?, ?, ?)",
        (user_id, message, response_text)
    )
    
    # Return response payload
    chat_record = query_db("SELECT * FROM Chats WHERE id = ?", (chat_id,), one=True)
    
    return jsonify({
        'id': chat_record['id'],
        'message': chat_record['message'],
        'response': chat_record['response'],
        'timestamp': chat_record['timestamp'],
        'saved': chat_record['saved']
    })

@chat_bp.route('/chatbot/search')
@login_required
def search_chats():
    """Search chat history based on query parameter."""
    user_id = session['user_id']
    query = request.args.get('q', '').strip()
    
    if not query:
        chats = query_db(
            "SELECT * FROM Chats WHERE user_id = ? ORDER BY timestamp ASC LIMIT 50",
            (user_id,)
        )
    else:
        chats = query_db(
            "SELECT * FROM Chats WHERE user_id = ? AND (message LIKE ? OR response LIKE ?) ORDER BY timestamp ASC",
            (user_id, f'%{query}%', f'%{query}%')
        )
        
    return jsonify([{
        'id': c['id'],
        'message': c['message'],
        'response': c['response'],
        'timestamp': c['timestamp'],
        'saved': c['saved']
    } for c in chats])

@chat_bp.route('/chatbot/delete/<int:chat_id>', methods=['POST', 'DELETE'])
@login_required
def delete_chat(chat_id):
    """Delete a specific chat record."""
    user_id = session['user_id']
    # Verify owner
    chat = query_db("SELECT id FROM Chats WHERE id = ? AND user_id = ?", (chat_id, user_id), one=True)
    if not chat:
        return jsonify({'error': 'Conversation not found or unauthorized.'}), 404
        
    execute_db("DELETE FROM Chats WHERE id = ?", (chat_id,))
    return jsonify({'success': True})

@chat_bp.route('/chatbot/save/<int:chat_id>', methods=['POST'])
@login_required
def toggle_save_chat(chat_id):
    """Toggle the bookmark/saved status of a specific chat."""
    user_id = session['user_id']
    chat = query_db("SELECT saved FROM Chats WHERE id = ? AND user_id = ?", (chat_id, user_id), one=True)
    if not chat:
        return jsonify({'error': 'Conversation not found or unauthorized.'}), 404
        
    new_status = 1 if chat['saved'] == 0 else 0
    execute_db("UPDATE Chats SET saved = ? WHERE id = ?", (new_status, chat_id))
    return jsonify({'success': True, 'saved': new_status})

@chat_bp.route('/chatbot/export')
@login_required
def export_chats():
    """Export all chats of the current user as a PDF."""
    user_id = session['user_id']
    chats = query_db(
        "SELECT message, response, timestamp FROM Chats WHERE user_id = ? ORDER BY timestamp ASC",
        (user_id,)
    )
    
    if not chats:
        # Return empty list indicator or warning
        return "No chat history available to export.", 400
        
    # Generate text report
    report_text = ""
    for chat in chats:
        ts = chat['timestamp']
        report_text += f"USER ({ts}):\n{chat['message']}\n\n"
        report_text += f"ADVO-BOT AI:\n{chat['response']}\n"
        report_text += "-"*60 + "\n\n"
        
    pdf_buffer = pdf_service.generate_pdf_from_text(report_text, title=f"Chat History - {session['name']}")
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"legal_assistant_chat_{datetime.date.today()}.pdf",
        mimetype='application/pdf'
    )

@chat_bp.route('/feedback/submit', methods=['POST'])
@login_required
def submit_feedback():
    """Submit a rating and comment for the chatbot or system."""
    user_id = session['user_id']
    rating = request.form.get('rating')
    comment = request.form.get('feedback', '').strip()
    
    if not rating:
        flash('Please select a rating.', 'danger')
        return redirect(request.referrer or url_for('chat.index'))
        
    try:
        rating_val = int(rating)
        if rating_val < 1 or rating_val > 5:
            raise ValueError()
    except ValueError:
        flash('Rating must be an integer between 1 and 5.', 'danger')
        return redirect(request.referrer or url_for('chat.index'))
        
    if not comment:
        flash('Please provide feedback comments.', 'danger')
        return redirect(request.referrer or url_for('chat.index'))
        
    execute_db(
        "INSERT INTO Feedback (user_id, rating, feedback) VALUES (?, ?, ?)",
        (user_id, rating_val, comment)
    )
    flash('Thank you for your feedback! Your submission has been saved.', 'success')
    return redirect(request.referrer or url_for('chat.index'))

@chat_bp.route('/chatbot/clear')
@login_required
def clear_conversation():
    """Clear all chat history for the current user to start a new conversation."""
    user_id = session['user_id']
    execute_db("DELETE FROM Chats WHERE user_id = ?", (user_id,))
    flash('Started a new conversation. Chat history cleared.', 'success')
    return redirect(url_for('chat.index'))
