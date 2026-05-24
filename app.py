from flask import Flask, render_template
from config import Config
from models.database import init_db
from routes.main import main_bp
from routes.auth import auth_bp
from routes.chat import chat_bp
from routes.dashboard import dashboard_bp
from routes.admin import admin_bp
from routes.features import features_bp
import os

def create_app():
    """Application factory to configure and initialize Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Register Blueprint routes
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(features_bp)
    
    # Configure custom error page handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content="<div class='container text-center' style='padding:100px 20px;'><i class='fa-solid fa-triangle-exclamation' style='font-size:4rem;color:var(--danger);'></i><h1 class='mt-3'>404 - Page Not Found</h1><p class='text-secondary mt-2'>The requested legal service or page does not exist.</p><a href='/' class='btn btn-primary mt-3'>Return Home</a></div>"), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', content="<div class='container text-center' style='padding:100px 20px;'><i class='fa-solid fa-server' style='font-size:4rem;color:var(--danger);'></i><h1 class='mt-3'>500 - Internal Server Error</h1><p class='text-secondary mt-2'>An error occurred within our reasoning engine. Please try again shortly.</p><a href='/' class='btn btn-primary mt-3'>Return Home</a></div>"), 500
        
    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('base.html', content="<div class='container text-center' style='padding:100px 20px;'><i class='fa-solid fa-file-circle-exclamation' style='font-size:4rem;color:var(--warning);'></i><h1 class='mt-3'>413 - File Too Large</h1><p class='text-secondary mt-2'>The uploaded document exceeds the 16MB file size limit.</p><a href='/document-analyzer' class='btn btn-primary mt-3'>Back to Doc Auditor</a></div>"), 413
        
    # Ensure no-cache headers are set for development
    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    # Initialize the database within app context
    with app.app_context():
        init_db()
        
    return app

app = create_app()

if __name__ == '__main__':
    # Determine port from env if available
    port = int(os.environ.get('PORT', 5000))
    # Run development server
    app.run(host='0.0.0.0', port=port, debug=True)
