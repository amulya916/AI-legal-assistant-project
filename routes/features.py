from flask import Blueprint, render_template, request, flash, redirect, url_for, session, send_file, jsonify, current_app
from models.database import execute_db, query_db
from utils.helpers import login_required
from utils.validators import allowed_file
from services import gemini_service, pdf_service
from werkzeug.utils import secure_filename
import os
import pypdf
import docx

features_bp = Blueprint('features', __name__)

# --- Helper Text Extractors ---
def extract_pdf_text(filepath):
    """Extract text from PDF file using pypdf."""
    text = ""
    try:
        reader = pypdf.PdfReader(filepath)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        text = f"Error reading PDF file content: {str(e)}"
    return text

def extract_docx_text(filepath):
    """Extract text from DOCX file using python-docx."""
    text = ""
    try:
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        text = f"Error reading DOCX file content: {str(e)}"
    return text

# --- 1. Legal Rights Finder ---
@features_bp.route('/rights-finder', methods=['GET', 'POST'])
@login_required
def rights_finder():
    """Analyze legal situations and list applicable rights and actions."""
    analysis = None
    situation = ""
    if request.method == 'POST':
        situation = request.form.get('situation', '').strip()
        if not situation:
            flash('Please describe your legal situation.', 'danger')
        else:
            # Query Gemini
            analysis = gemini_service.analyze_legal_situation(situation)
            
    return render_template('rights_finder.html', situation=situation, analysis=analysis)

# --- 2. RTI Assistant ---
@features_bp.route('/rti-assistant')
@login_required
def rti_assistant():
    """Render guides, FAQs, and application templates for RTI filing."""
    return render_template('rti_assistant.html')

# --- 3. Legal Notice Generator ---
@features_bp.route('/notice-generator', methods=['GET', 'POST'])
@login_required
def notice_generator():
    """Form to customize and trigger AI Legal Notice drafting."""
    generated_text = None
    notice_id = None
    notice_type = None
    
    if request.method == 'POST':
        notice_type = request.form.get('notice_type')
        
        # Read variables based on notice type
        form_data = {}
        for key in request.form.keys():
            if key != 'notice_type':
                form_data[key] = request.form.get(key)
                
        if not notice_type:
            flash('Please select a valid notice type.', 'danger')
        else:
            # Generate notice draft
            generated_text = gemini_service.generate_legal_notice(notice_type, form_data)
            
            # Save notice draft in SQLite
            notice_id = execute_db(
                "INSERT INTO Legal_Notices (user_id, notice_type, generated_text) VALUES (?, ?, ?)",
                (session['user_id'], notice_type, generated_text)
            )
            
    # Load previously generated notices for this user
    notices_history = query_db(
        "SELECT * FROM Legal_Notices WHERE user_id = ? ORDER BY created_at DESC",
        (session['user_id'],)
    )
    
    return render_template(
        'notice_generator.html',
        generated_text=generated_text,
        notice_id=notice_id,
        notice_type=notice_type,
        notices_history=notices_history
    )

@features_bp.route('/notice/save', methods=['POST'])
@login_required
def save_notice():
    """Allows user to update / save their manual edits to a notice draft."""
    data = request.get_json()
    notice_id = data.get('notice_id')
    generated_text = data.get('generated_text')
    
    if not notice_id or not generated_text:
        return jsonify({'error': 'Notice ID and edited content are required.'}), 400
        
    # Verify ownership
    notice = query_db("SELECT id FROM Legal_Notices WHERE id = ? AND user_id = ?", (notice_id, session['user_id']), one=True)
    if not notice:
        return jsonify({'error': 'Document not found or unauthorized.'}), 404
        
    execute_db("UPDATE Legal_Notices SET generated_text = ? WHERE id = ?", (generated_text, notice_id))
    return jsonify({'success': True, 'message': 'Notice draft saved successfully.'})

@features_bp.route('/notice/download/<int:notice_id>')
@login_required
def download_notice(notice_id):
    """Generates and serves a formatted PDF file of the selected notice."""
    notice = query_db(
        "SELECT notice_type, generated_text FROM Legal_Notices WHERE id = ? AND user_id = ?",
        (notice_id, session['user_id']),
        one=True
    )
    
    if not notice:
        flash('Requested notice does not exist.', 'danger')
        return redirect(url_for('features.notice_generator'))
        
    pdf_buffer = pdf_service.generate_pdf_from_text(
        notice['generated_text'],
        title=f"LEGAL NOTICE: {notice['notice_type'].replace('_', ' ').upper()}"
    )
    
    clean_title = notice['notice_type'].lower().replace(' ', '_')
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"{clean_title}_notice_{notice_id}.pdf",
        mimetype='application/pdf'
    )

# --- 4. Document Analyzer ---
@features_bp.route('/document-analyzer', methods=['GET', 'POST'])
@login_required
def document_analyzer():
    """Allows user to upload PDF/DOCX files, extract text, and receive Gemini analysis."""
    analysis = None
    filename = None
    
    if request.method == 'POST':
        # Check file
        if 'document' not in request.files:
            flash('No file upload part selected.', 'danger')
            return redirect(request.url)
            
        file = request.files['document']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            # Safe save
            filename = secure_filename(file.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(upload_path)
            
            # Extract content
            ext = filename.rsplit('.', 1)[1].lower()
            extracted_text = ""
            if ext == 'pdf':
                extracted_text = extract_pdf_text(upload_path)
            elif ext == 'docx':
                extracted_text = extract_docx_text(upload_path)
                
            if not extracted_text.strip() or "Error reading" in extracted_text:
                flash('Unable to extract text content from this document.', 'danger')
                if os.path.exists(upload_path):
                    os.remove(upload_path)
                return redirect(request.url)
                
            # Submit text to Gemini
            analysis_markdown = gemini_service.analyze_document(extracted_text)
            
            # Parse analysis sections
            # We'll save the analysis as simple markdown in db columns or separate it
            summary = ""
            key_points = ""
            simplified = ""
            
            # Parse sections if structured, otherwise dump whole text into summary
            sections = analysis_markdown.split('###')
            if len(sections) > 1:
                summary = analysis_markdown # Keep markdown intact
            else:
                summary = analysis_markdown
                
            # Save document log in SQLite
            execute_db(
                "INSERT INTO Uploaded_Documents (user_id, file_name, summary, key_points, simplified) VALUES (?, ?, ?, ?, ?)",
                (session['user_id'], filename, summary, key_points, simplified)
            )
            analysis = analysis_markdown
            flash('Document processed successfully.', 'success')
            
            # Clean up uploaded file from local filesystem after processing to conserve disk space
            if os.path.exists(upload_path):
                os.remove(upload_path)
        else:
            flash('Invalid file format. Only PDF and DOCX documents are accepted.', 'danger')
            
    # Load upload history
    uploads_history = query_db(
        "SELECT * FROM Uploaded_Documents WHERE user_id = ? ORDER BY upload_date DESC",
        (session['user_id'],)
    )
    
    return render_template(
        'document_analyzer.html',
        analysis=analysis,
        filename=filename,
        uploads_history=uploads_history
    )
