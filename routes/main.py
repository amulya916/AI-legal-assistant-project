from flask import Blueprint, render_template, request, flash, redirect, url_for

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Render home landing page."""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """Render details about the system and authors."""
    return render_template('about.html')

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """Render contact page and process form submission."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        if not name or not email or not message:
            flash('All fields are required.', 'danger')
            return redirect(url_for('main.contact'))
            
        flash('Thank you for contacting us! Our team will get back to you shortly.', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('contact.html')
