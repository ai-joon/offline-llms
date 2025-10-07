#!/usr/bin/env python3
"""
Start the React frontend development server
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Change to frontend directory
    frontend_dir = Path(__file__).parent / "frontend"
    os.chdir(frontend_dir)
    
    # Install dependencies if needed
    print("🔧 Installing frontend dependencies...")
    subprocess.run(["npm", "install"], check=True)
    
    # Start the development server
    print("🚀 Starting React frontend development server...")
    subprocess.run(["npm", "start"])

if __name__ == "__main__":
    main()
