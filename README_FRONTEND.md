# AI Chatbot - Advanced React Frontend

A modern, dark-themed React frontend for the AI Chatbot with Document RAG capabilities.

## 🎨 Features

- **Modern Dark Theme** - Sleek, professional dark UI with smooth animations
- **Real-time Chat Interface** - Stream messages with typing indicators
- **PDF Viewer** - Integrated PDF viewer with pagination controls
- **Document Management** - Select and switch between PDF documents
- **Advanced Settings** - Configure retrieval parameters and display options
- **Responsive Design** - Works on desktop, tablet, and mobile devices
- **Context Display** - Show source documents and page references
- **Copy to Clipboard** - Easy message copying functionality

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.11+ with the backend running
- Ollama running locally

### Installation

1. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start the Development Server**
   ```bash
   npm start
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## 🏗️ Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── Sidebar.tsx          # Document selection & settings
│   │   ├── ChatInterface.tsx    # Main chat interface
│   │   └── PDFViewer.tsx        # PDF viewer component
│   ├── services/
│   │   └── api.ts               # API service layer
│   ├── types/
│   │   └── index.ts             # TypeScript type definitions
│   ├── App.tsx                  # Main application component
│   ├── App.css                  # Application styles
│   ├── index.tsx                # Application entry point
│   └── index.css                # Global styles
├── package.json
└── tsconfig.json
```

## 🎯 Key Components

### Sidebar
- **Document Selection**: Choose from available PDF documents
- **Settings Panel**: Configure retrieval parameters
- **Status Indicators**: Show current document and loading states
- **Action Buttons**: Clear chat, toggle settings

### Chat Interface
- **Message Display**: User and AI messages with timestamps
- **Markdown Support**: Rich text rendering with syntax highlighting
- **Source Display**: Show document sources and page references
- **Typing Indicators**: Visual feedback during AI response generation
- **Copy Functionality**: Easy message copying

### PDF Viewer
- **Document Display**: Embedded PDF viewer with iframe
- **Pagination Controls**: Navigate through PDF pages
- **Download Option**: Download the current PDF
- **Responsive Layout**: Adapts to different screen sizes

## 🎨 Design System

### Color Palette
- **Background**: `#0a0a0a` (Deep black)
- **Surface**: `#1a1a1a` (Dark gray)
- **Border**: `#2a2a2a` (Medium gray)
- **Text Primary**: `#e5e5e5` (Light gray)
- **Text Secondary**: `#a3a3a3` (Medium gray)
- **Accent**: `#3b82f6` (Blue)

### Typography
- **Font Family**: System fonts (SF Pro, Segoe UI, Roboto)
- **Headings**: 700 weight, various sizes
- **Body**: 400 weight, 0.875rem base size
- **Code**: Courier New monospace

### Animations
- **Framer Motion**: Smooth transitions and micro-interactions
- **Hover Effects**: Subtle scale and color transitions
- **Loading States**: Spinning indicators and progress feedback

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

### API Integration
The frontend communicates with the FastAPI backend through:
- **REST API**: HTTP requests for data
- **WebSocket**: Real-time updates (future enhancement)
- **File Upload**: PDF document handling

## 📱 Responsive Design

### Breakpoints
- **Desktop**: 1024px+ (Full layout)
- **Tablet**: 768px-1023px (Stacked layout)
- **Mobile**: <768px (Single column)

### Mobile Features
- Collapsible sidebar
- Touch-friendly controls
- Optimized PDF viewer
- Swipe gestures (future)

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Docker (Optional)
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🔍 Development

### Available Scripts
- `npm start` - Start development server
- `npm build` - Create production build
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Code Quality
- **TypeScript**: Full type safety
- **ESLint**: Code linting
- **Prettier**: Code formatting (recommended)

## 🎯 Future Enhancements

- [ ] Real-time WebSocket communication
- [ ] Voice input/output
- [ ] Document annotation
- [ ] Chat history persistence
- [ ] User authentication
- [ ] Multi-language support
- [ ] Advanced PDF features
- [ ] Export chat conversations

## 🐛 Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure backend is running on port 8000
   - Check CORS settings in backend

2. **PDF Not Loading**
   - Verify PDF files exist in `docx/` directory
   - Check file permissions

3. **Build Errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility

### Debug Mode
Set `REACT_APP_DEBUG=true` in `.env` for additional logging.

## 📄 License

This project is part of the AI Chatbot system. See main README for license information.
