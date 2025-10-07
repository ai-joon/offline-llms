#!/usr/bin/env python3
"""
Complete setup script for the AI Chatbot React Frontend
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a command and handle errors"""
    print(f"🔧 Running: {' '.join(command)}")
    try:
        # For npm commands on Windows, use the full path
        if command[0] == "npm" and os.name == 'nt':
            command[0] = r"C:\Program Files\nodejs\npm.cmd"
        
        result = subprocess.run(command, cwd=cwd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        sys.exit(1)

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Node.js
    try:
        result = run_command(["node", "--version"], check=False)
        if result.returncode != 0:
            print("❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/")
            sys.exit(1)
        print(f"✅ Node.js version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/")
        sys.exit(1)
    
    # Check npm
    try:
        result = run_command(["npm", "--version"], check=False)
        if result.returncode != 0:
            print("❌ npm not found. Please install npm")
            sys.exit(1)
        print(f"✅ npm version: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ npm not found. Please install npm")
        sys.exit(1)

def setup_frontend():
    """Setup the React frontend"""
    print("\n🚀 Setting up React frontend...")
    
    frontend_dir = Path("frontend")
    
    # Create frontend directory if it doesn't exist
    frontend_dir.mkdir(exist_ok=True)
    
    # Check if package.json exists
    if not (frontend_dir / "package.json").exists():
        print("❌ package.json not found. Please ensure the frontend files are in place.")
        sys.exit(1)
    
    # Install dependencies
    print("📦 Installing frontend dependencies...")
    run_command(["npm", "install"], cwd=frontend_dir)
    
    # Create .env file if it doesn't exist
    env_file = frontend_dir / ".env"
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(env_file, "w") as f:
            f.write("REACT_APP_API_URL=http://localhost:8000\n")
    
    print("✅ Frontend setup complete!")

def setup_backend():
    """Setup the FastAPI backend"""
    print("\n🚀 Setting up FastAPI backend...")
    
    backend_dir = Path("backend")
    
    # Check if backend directory exists
    if not backend_dir.exists():
        print("❌ Backend directory not found. Please ensure the backend files are in place.")
        sys.exit(1)
    
    # Install Python dependencies
    print("📦 Installing backend dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=backend_dir)
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("📝 Creating .env file...")
        with open(env_file, "w") as f:
            f.write("""# API Settings
API_TITLE=AI Chatbot API
API_VERSION=1.0.0
DEBUG=false

# CORS Settings
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Ollama Settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
OLLAMA_LLM_MODEL=qwen2.5:3b-instruct

# FAISS Settings
FAISS_INDEX_DIR=faiss_indices
FAISS_GLOBAL_INDEX_DIR=faiss_index

# PDF Settings
PDF_DIRECTORY=docx
MAX_PDF_SIZE=104857600

# Chat Settings
DEFAULT_TOP_K=4
DEFAULT_MAX_TOKENS=256
DEFAULT_MAX_CONTEXT_CHARS=4000
DEFAULT_RETRIEVAL_MODE=similarity

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
""")
    
    print("✅ Backend setup complete!")

def create_startup_scripts():
    """Create startup scripts for easy development"""
    print("\n📝 Creating startup scripts...")
    
    # Create start_frontend.bat for Windows
    with open("start_frontend.bat", "w") as f:
        f.write("""@echo off
echo Starting React Frontend...
cd frontend
npm start
pause
""")
    
    # Create start_backend.bat for Windows
    with open("start_backend.bat", "w") as f:
        f.write("""@echo off
echo Starting FastAPI Backend...
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
""")
    
    # Create start_frontend.sh for Unix/Linux/Mac
    with open("start_frontend.sh", "w") as f:
        f.write("""#!/bin/bash
echo "Starting React Frontend..."
cd frontend
npm start
""")
    
    # Create start_backend.sh for Unix/Linux/Mac
    with open("start_backend.sh", "w") as f:
        f.write("""#!/bin/bash
echo "Starting FastAPI Backend..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
""")
    
    # Make shell scripts executable
    if os.name != 'nt':  # Not Windows
        os.chmod("start_frontend.sh", 0o755)
        os.chmod("start_backend.sh", 0o755)
    
    print("✅ Startup scripts created!")

def main():
    """Main setup function"""
    print("🎯 AI Chatbot Frontend Setup")
    print("=" * 40)
    
    # Check requirements
    check_requirements()
    
    # Setup frontend
    setup_frontend()
    
    # Setup backend
    setup_backend()
    
    # Create startup scripts
    create_startup_scripts()
    
    print("\n🎉 Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Make sure Ollama is running: ollama serve")
    print("2. Start the backend: python start_backend.py")
    print("3. Start the frontend: python start_frontend.py")
    print("4. Open http://localhost:3000 in your browser")
    print("\n💡 Or use the batch/shell scripts:")
    print("   - Windows: start_backend.bat & start_frontend.bat")
    print("   - Unix/Linux/Mac: ./start_backend.sh & ./start_frontend.sh")

if __name__ == "__main__":
    main()
