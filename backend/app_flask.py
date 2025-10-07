from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import psutil
import os
import sys
from pathlib import Path

# Add project root to path to access loader.py and other modules
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import settings
from core.database import get_db, set_db, get_current_pdf_path, initialize_db
from services.chat_service import ChatService
from services.pdf_service import PDFService
from services.index_service import IndexService

app = Flask(__name__)

# Fix PDF directory path to use absolute path from project root
settings.pdf_directory = str(PROJECT_ROOT / "docx")
settings.faiss_index_dir = str(PROJECT_ROOT / "faiss_indices")
settings.faiss_global_index_dir = str(PROJECT_ROOT / "faiss_index")

# CORS configuration
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
], supports_credentials=True)

# Initialize on startup
with app.app_context():
    import asyncio
    asyncio.run(initialize_db())
    print("Database initialized")
    print("AI Chatbot API started successfully!")

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
        }
    })

# PDF endpoints
@app.route('/api/pdfs', methods=['GET'])
def get_available_pdfs():
    """Get list of available PDF documents"""
    try:
        pdf_service = PDFService()
        import asyncio
        pdfs = asyncio.run(pdf_service.get_available_pdfs())
        return jsonify([{"name": p.name, "path": p.path} for p in pdfs])
    except Exception as e:
        return jsonify({"error": f"Failed to load PDFs: {str(e)}"}), 500

@app.route('/api/load-pdf', methods=['POST'])
def load_pdf():
    """Load or create index for a specific PDF"""
    try:
        data = request.get_json()
        pdf_path = data.get('pdf_path')
        
        if not pdf_path:
            return jsonify({"error": "pdf_path is required"}), 400
        
        # Validate PDF exists
        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF file not found"}), 404
        
        # Check if it's already loaded
        current_pdf = get_current_pdf_path()
        if current_pdf == pdf_path:
            return jsonify({
                "success": True,
                "message": "PDF already loaded",
                "pdf_path": pdf_path
            })
        
        # Load or create index
        index_service = IndexService()
        import asyncio
        db = asyncio.run(index_service.get_or_create_pdf_index(pdf_path))
        
        # Set as current database
        set_db(db, pdf_path)
        
        return jsonify({
            "success": True,
            "message": f"Successfully loaded {os.path.basename(pdf_path)}",
            "pdf_path": pdf_path
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to load PDF: {str(e)}"}), 500

@app.route('/api/pdf-content', methods=['GET'])
def get_pdf_content():
    """Get PDF file content for viewing"""
    try:
        path = request.args.get('path')
        
        if not path or not os.path.exists(path):
            return jsonify({"error": "PDF file not found"}), 404
        
        # Security check - ensure path is within allowed directory
        pdf_dir = Path(settings.pdf_directory).resolve()
        pdf_path = Path(path).resolve()
        
        if not str(pdf_path).startswith(str(pdf_dir)):
            return jsonify({"error": "Access denied"}), 403
        
        return send_file(path, mimetype='application/pdf', as_attachment=False)
        
    except Exception as e:
        return jsonify({"error": f"Failed to load PDF content: {str(e)}"}), 500

@app.route('/api/pdf-info/<pdf_name>', methods=['GET'])
def get_pdf_info(pdf_name):
    """Get detailed information about a specific PDF"""
    try:
        pdf_service = PDFService()
        import asyncio
        pdf_info = asyncio.run(pdf_service.get_pdf_info(pdf_name))
        return jsonify(pdf_info)
    except Exception as e:
        return jsonify({"error": f"Failed to get PDF info: {str(e)}"}), 500

# Chat endpoints
@app.route('/api/chat', methods=['POST'])
def send_message():
    """Send a message to the AI chatbot"""
    try:
        data = request.get_json()
        message = data.get('message')
        chat_settings = data.get('settings', {})
        
        if not message:
            return jsonify({"error": "message is required"}), 400
        
        # Get current database
        db = get_db()
        current_pdf = get_current_pdf_path()
        
        # Initialize chat service
        chat_service = ChatService()
        
        # Process the message
        import asyncio
        response = asyncio.run(chat_service.process_message(
            message=message,
            db=db,
            settings=chat_settings,
            current_pdf=current_pdf
        ))
        
        return jsonify({
            "answer": response.answer,
            "sources": [{"content": s.content, "metadata": s.metadata} for s in response.sources]
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to process message: {str(e)}"}), 500

@app.route('/api/chat/history', methods=['GET'])
def get_chat_history():
    """Get chat history (placeholder for future implementation)"""
    return jsonify({"message": "Chat history feature coming soon"})

@app.route('/api/chat/history', methods=['DELETE'])
def clear_chat_history():
    """Clear chat history (placeholder for future implementation)"""
    return jsonify({"message": "Chat history cleared"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', '16005'))
    print(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)

