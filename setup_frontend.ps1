# AI Chatbot Frontend Setup Script
Write-Host "🎯 AI Chatbot Frontend Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

Write-Host "🔍 Checking requirements..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 16+ from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check npm using full path
try {
    $npmVersion = & "C:\Program Files\nodejs\npm.cmd" --version
    Write-Host "✅ npm version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm not found. Please install npm" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Setting up React frontend..." -ForegroundColor Yellow

# Create frontend directory if it doesn't exist
if (!(Test-Path "frontend")) {
    New-Item -ItemType Directory -Name "frontend"
}

# Check if package.json exists
if (!(Test-Path "frontend\package.json")) {
    Write-Host "❌ package.json not found. Please ensure the frontend files are in place." -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
try {
    & "C:\Program Files\nodejs\npm.cmd" install
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install frontend dependencies" -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    "REACT_APP_API_URL=http://localhost:8000" | Out-File -FilePath ".env" -Encoding UTF8
}

Set-Location ..
Write-Host "✅ Frontend setup complete!" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Setting up FastAPI backend..." -ForegroundColor Yellow

# Check if backend directory exists
if (!(Test-Path "backend")) {
    Write-Host "❌ Backend directory not found. Please ensure the backend files are in place." -ForegroundColor Red
    exit 1
}

# Install Python dependencies
Write-Host "📦 Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
try {
    python -m pip install -r requirements.txt
    Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}

# Create .env file if it doesn't exist
if (!(Test-Path ".env")) {
    Write-Host "📝 Creating .env file..." -ForegroundColor Yellow
    @"
# API Settings
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
"@ | Out-File -FilePath ".env" -Encoding UTF8
}

Set-Location ..
Write-Host "✅ Backend setup complete!" -ForegroundColor Green

Write-Host ""
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Make sure Ollama is running: ollama serve" -ForegroundColor White
Write-Host "2. Start the backend: .\start_backend.bat" -ForegroundColor White
Write-Host "3. Start the frontend: .\start_frontend.bat" -ForegroundColor White
Write-Host "4. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

