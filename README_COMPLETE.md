# AI Chatbot - Complete React Frontend & FastAPI Backend

A modern, full-stack AI chatbot application with document RAG capabilities, featuring a sleek React frontend and robust FastAPI backend.

## 🎯 Overview

This project replaces the Streamlit interface with a professional React frontend while maintaining all the original functionality:

- **Document RAG**: Chat with AI about your PDF documents
- **Dynamic Index Management**: Automatic FAISS index creation per document
- **Modern UI**: Dark-themed, responsive React interface
- **Real-time Chat**: Stream messages with typing indicators
- **PDF Viewer**: Integrated document viewer with pagination
- **Advanced Settings**: Configure retrieval parameters

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │   Ollama LLM    │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│  (Port 11434)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Viewer    │    │  FAISS Indices  │    │  Embeddings     │
│   (Client-side) │    │  (Per Document) │    │  (nomic-embed)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js 16+** and npm
- **Python 3.11+** with pip
- **Ollama** running locally
- **Git** (for cloning)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd ai-chatbot

# Run the complete setup
python setup_frontend.py
```

### 2. Start Ollama

```bash
# Start Ollama server
ollama serve

# Pull required models (in another terminal)
ollama pull nomic-embed-text
ollama pull qwen2.5:3b-instruct
```

### 3. Start the Application

**Option A: Using Python scripts**
```bash
# Terminal 1 - Backend
python start_backend.py

# Terminal 2 - Frontend  
python start_frontend.py
```

**Option B: Using batch/shell scripts**
```bash
# Windows
start_backend.bat
start_frontend.bat

# Unix/Linux/Mac
./start_backend.sh
./start_frontend.sh
```

**Option C: Manual start**
```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm install
npm start
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Project Structure

```
ai-chatbot/
├── frontend/                 # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API service layer
│   │   ├── types/           # TypeScript definitions
│   │   └── ...
│   ├── package.json
│   └── tsconfig.json
├── backend/                  # FastAPI backend
│   ├── api/
│   │   └── routes/          # API endpoints
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   └── database.py      # Database management
│   ├── services/            # Business logic
│   ├── models/              # Pydantic models
│   ├── main.py              # FastAPI app
│   └── requirements.txt
├── faiss_indices/           # Per-document FAISS indices
├── docx/                    # PDF documents
├── loader.py                # Original loader functions
├── interface.py             # Original Streamlit interface
└── setup_frontend.py        # Complete setup script
```

## 🎨 Frontend Features

### Modern Dark Theme
- **Color Palette**: Deep blacks, grays, and blue accents
- **Typography**: System fonts with proper hierarchy
- **Animations**: Smooth transitions with Framer Motion
- **Responsive**: Works on desktop, tablet, and mobile

### Chat Interface
- **Real-time Messaging**: Stream AI responses
- **Markdown Support**: Rich text with syntax highlighting
- **Source Display**: Show document sources and page references
- **Copy Functionality**: Easy message copying
- **Typing Indicators**: Visual feedback during generation

### Document Management
- **PDF Selection**: Choose from available documents
- **Auto-indexing**: Automatic FAISS index creation
- **PDF Viewer**: Integrated viewer with pagination
- **Download Option**: Download current PDF

### Advanced Settings
- **Retrieval Parameters**: Top-k, MMR, context size
- **Model Settings**: Max tokens, temperature
- **Display Options**: Show/hide context sources

## 🔧 Backend Features

### FastAPI Backend
- **RESTful API**: Clean, documented endpoints
- **CORS Support**: Cross-origin requests
- **Error Handling**: Comprehensive error responses
- **Type Safety**: Pydantic models throughout

### Document Processing
- **PDF Loading**: Automatic document discovery
- **Index Management**: Per-document FAISS indices
- **Metadata Extraction**: PDF information and statistics
- **Security**: Path validation and access control

### AI Integration
- **Ollama Integration**: Local LLM inference
- **Context Retrieval**: Smart document search
- **Response Generation**: Context-aware responses
- **Fallback Handling**: General knowledge when no context

## 🔌 API Endpoints

### Health & Status
- `GET /api/health` - System health check

### Document Management
- `GET /api/pdfs` - List available PDFs
- `POST /api/load-pdf` - Load/create index for PDF
- `GET /api/pdf-content` - Get PDF file content
- `GET /api/pdf-info/{name}` - Get PDF metadata

### Chat
- `POST /api/chat` - Send message to AI
- `GET /api/chat/history` - Get chat history (future)
- `DELETE /api/chat/history` - Clear chat history (future)

## ⚙️ Configuration

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000
```

### Backend (.env)
```env
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
```

## 🚀 Deployment

### Development
```bash
# Start both services
python start_backend.py & python start_frontend.py
```

### Production
```bash
# Build frontend
cd frontend
npm run build

# Serve with nginx or similar
# Backend can be deployed with gunicorn
```

### Docker (Optional)
```dockerfile
# Frontend
FROM node:18-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

# Backend
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY backend/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 Development

### Frontend Development
```bash
cd frontend
npm start          # Development server
npm run build      # Production build
npm test           # Run tests
npm run lint       # Lint code
```

### Backend Development
```bash
cd backend
python -m uvicorn main:app --reload  # Development server
python -m pytest                    # Run tests
python -m black .                   # Format code
```

### Code Quality
- **TypeScript**: Full type safety in frontend
- **Pydantic**: Type validation in backend
- **ESLint**: Code linting
- **Black**: Python code formatting

## 🐛 Troubleshooting

### Common Issues

1. **Frontend won't start**
   - Check Node.js version (16+)
   - Clear node_modules and reinstall
   - Check for port conflicts (3000)

2. **Backend won't start**
   - Check Python version (3.11+)
   - Install dependencies: `pip install -r requirements.txt`
   - Check for port conflicts (8000)

3. **Ollama connection failed**
   - Ensure Ollama is running: `ollama serve`
   - Check models are pulled: `ollama list`
   - Verify port 11434 is accessible

4. **PDF not loading**
   - Check PDF files exist in `docx/` directory
   - Verify file permissions
   - Check file size limits

5. **CORS errors**
   - Ensure backend CORS settings include frontend URL
   - Check environment variables

### Debug Mode
```bash
# Frontend
REACT_APP_DEBUG=true npm start

# Backend
DEBUG=true python -m uvicorn main:app --reload
```

## 📈 Performance

### Optimization Tips
- **Frontend**: Use React.memo for expensive components
- **Backend**: Implement response caching
- **FAISS**: Use appropriate chunk sizes
- **Ollama**: Adjust model parameters

### Monitoring
- **Health Check**: `/api/health` endpoint
- **System Metrics**: CPU, memory, disk usage
- **API Performance**: Response times and error rates

## 🔮 Future Enhancements

### Planned Features
- [ ] Real-time WebSocket communication
- [ ] Voice input/output
- [ ] Document annotation
- [ ] Chat history persistence
- [ ] User authentication
- [ ] Multi-language support
- [ ] Advanced PDF features
- [ ] Export chat conversations
- [ ] Batch document processing
- [ ] API rate limiting
- [ ] Response streaming

### Technical Improvements
- [ ] Redis caching
- [ ] Database persistence
- [ ] Microservices architecture
- [ ] Kubernetes deployment
- [ ] Monitoring and logging
- [ ] Automated testing
- [ ] CI/CD pipeline

## 📄 License

This project is part of the AI Chatbot system. See the main repository for license information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check the GitHub issues
4. Create a new issue with details

---

**Happy Chatting! 🚀**
