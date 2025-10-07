@echo off
echo 🎯 AI Chatbot Frontend Setup
echo ================================

echo 🔍 Checking requirements...

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)
echo ✅ Node.js found

REM Check npm
"C:\Program Files\nodejs\npm.cmd" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm not found. Please install npm
    pause
    exit /b 1
)
echo ✅ npm found

echo.
echo 🚀 Setting up React frontend...

REM Create frontend directory if it doesn't exist
if not exist "frontend" mkdir frontend

REM Check if package.json exists
if not exist "frontend\package.json" (
    echo ❌ package.json not found. Please ensure the frontend files are in place.
    pause
    exit /b 1
)

REM Install dependencies
echo 📦 Installing frontend dependencies...
cd frontend
"C:\Program Files\nodejs\npm.cmd" install
if %errorlevel% neq 0 (
    echo ❌ Failed to install frontend dependencies
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    echo REACT_APP_API_URL=http://localhost:8000 > .env
)

cd ..
echo ✅ Frontend setup complete!

echo.
echo 🚀 Setting up FastAPI backend...

REM Check if backend directory exists
if not exist "backend" (
    echo ❌ Backend directory not found. Please ensure the backend files are in place.
    pause
    exit /b 1
)

REM Install Python dependencies
echo 📦 Installing backend dependencies...
cd backend
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install backend dependencies
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file...
    (
        echo # API Settings
        echo API_TITLE=AI Chatbot API
        echo API_VERSION=1.0.0
        echo DEBUG=false
        echo.
        echo # CORS Settings
        echo CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
        echo.
        echo # Ollama Settings
        echo OLLAMA_HOST=http://localhost:11434
        echo OLLAMA_EMBED_MODEL=nomic-embed-text
        echo OLLAMA_LLM_MODEL=qwen2.5:3b-instruct
        echo.
        echo # FAISS Settings
        echo FAISS_INDEX_DIR=faiss_indices
        echo FAISS_GLOBAL_INDEX_DIR=faiss_index
        echo.
        echo # PDF Settings
        echo PDF_DIRECTORY=docx
        echo MAX_PDF_SIZE=104857600
        echo.
        echo # Chat Settings
        echo DEFAULT_TOP_K=4
        echo DEFAULT_MAX_TOKENS=256
        echo DEFAULT_MAX_CONTEXT_CHARS=4000
        echo DEFAULT_RETRIEVAL_MODE=similarity
        echo.
        echo # Security
        echo SECRET_KEY=your-secret-key-change-in-production
        echo ACCESS_TOKEN_EXPIRE_MINUTES=30
    ) > .env
)

cd ..
echo ✅ Backend setup complete!

echo.
echo 🎉 Setup Complete!
echo.
echo 📋 Next Steps:
echo 1. Make sure Ollama is running: ollama serve
echo 2. Start the backend: start_backend.bat
echo 3. Start the frontend: start_frontend.bat
echo 4. Open http://localhost:3000 in your browser
echo.
pause

