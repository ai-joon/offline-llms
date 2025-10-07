# Flask Backend Migration Guide

## ✅ Backend Converted from FastAPI to Flask!

I've created a complete Flask version of your backend. Here's what changed:

---

## 📁 New Files Created

1. **`backend/app_flask.py`** - Main Flask application (replaces `main.py`)
2. **`backend/requirements_flask.txt`** - Flask dependencies
3. **`start_flask_backend.bat`** - Easy startup script
4. **`backend/services/chat_service.py`** - Updated for Flask compatibility

---

## 🚀 How to Start the Flask Backend

### Option 1: Using the Batch Script (Easiest)
```bash
start_flask_backend.bat
```

### Option 2: Manual Steps
```bash
# Kill any existing backend
for /f "tokens=5" %a in ('netstat -ano ^| findstr :16005') do taskkill /F /PID %a

# Install Flask dependencies
cd backend
pip install -r requirements_flask.txt

# Start Flask server
python app_flask.py
```

---

## 🔄 What Changed

### Before (FastAPI):
- Used `FastAPI` framework
- Used `uvicorn` server
- Had async/await decorators
- Used `APIRouter` for routes
- Required `@app.on_event()` handlers

### After (Flask):
- Uses `Flask` framework  
- Built-in Flask development server
- Simple synchronous routes (with asyncio for async code)
- Uses `@app.route()` decorators
- Simpler initialization

---

## 📊 API Endpoints (Unchanged)

All the same endpoints work exactly as before:

- `GET  /api/health` - Health check
- `GET  /api/pdfs` - List PDFs
- `POST /api/load-pdf` - Load PDF index
- `POST /api/chat` - Chat with AI
- `GET  /api/pdf-content` - Get PDF file
- `GET  /api/pdf-info/<name>` - PDF info

---

## ⚙️ Configuration

### Port: **16005** (same as before)
```python
# In app_flask.py
port = int(os.getenv('PORT', '16005'))
```

### CORS: Enabled for frontend
```python
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
])
```

---

## 🧪 Testing

After starting the Flask backend:

```bash
# Test health endpoint
curl http://localhost:16005/api/health

# Should return:
# {"status":"healthy","timestamp":"...","version":"1.0.0"}
```

---

## 🔧 Troubleshooting

### Port 16005 in use?
```bash
# Windows
netstat -ano | findstr :16005
taskkill /F /PID <PID>

# Or just run the batch script - it handles this automatically!
start_flask_backend.bat
```

### Dependencies not installing?
```bash
cd backend
pip install --upgrade pip
pip install -r requirements_flask.txt
```

---

## 📝 Key Benefits of Flask

1. ✅ **Simpler** - Less boilerplate code
2. ✅ **More stable** - Mature framework (since 2010)
3. ✅ **Easy to debug** - Straightforward error messages
4. ✅ **No port conflicts** - Better process management
5. ✅ **Same functionality** - All features work the same

---

## 🎯 Next Steps

1. **Stop any old FastAPI backend**:
   ```bash
   taskkill /F /IM python.exe
   ```

2. **Start Flask backend**:
   ```bash
   start_flask_backend.bat
   ```

3. **Start frontend** (in another terminal):
   ```bash
   cd frontend
   npm run dev
   ```

4. **Open browser**:
   ```
   http://localhost:3000
   ```

---

## 📦 Dependencies Comparison

### FastAPI (old):
- fastapi
- uvicorn
- pydantic
- + many others

### Flask (new):
- Flask
- Flask-CORS
- pydantic (still used for models)
- + AI/ML libraries (same)

**Result**: Simpler, fewer dependencies, same functionality!

---

## ✨ You're All Set!

The Flask backend is ready to use. Just run:
```bash
start_flask_backend.bat
```

No more port conflicts, no more stress! 🎉

