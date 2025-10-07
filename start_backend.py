#!/usr/bin/env python3
"""
Start the FastAPI backend server
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Install dependencies if needed
    print("🔧 Installing backend dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Start the server
    print("🚀 Starting FastAPI backend server...")
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])

if __name__ == "__main__":
    main()
