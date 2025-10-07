import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'

type ChatSettings = {
  topK: number
  retrievalMode: string
  maxTokens: number
  maxContextChars: number
  showContext: boolean
}

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
  sources?: ChatSource[]
}

type ChatSource = { content: string; metadata: Record<string, unknown> }
type ChatResponse = { answer: string; sources: ChatSource[] }
type PDFDocument = { name: string; path: string }

const API_BASE = (import.meta as any).env.VITE_API_BASE ?? 'http://localhost:8000/api'

function useApiBase() {
  return useMemo(() => API_BASE.replace(/\/$/, ''), [])
}

function ThemeToggle() {
  const [theme, setTheme] = useState<string>(() => localStorage.getItem('theme') || 'dark')
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])
  return (
    <label className="swap swap-rotate">
      <input
        type="checkbox"
        checked={theme === 'dark'}
        onChange={(e) => setTheme(e.target.checked ? 'dark' : 'light')}
      />
      <svg className="swap-on fill-current w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path d="M5.64 17.657A9 9 0 1118 6a7 7 0 10-12.36 11.657z" />
      </svg>
      <svg className="swap-off fill-current w-6 h-6" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
        <path d="M5 12a7 7 0 1114 0 7 7 0 01-14 0zm7-10v4m0 12v4m10-10h-4M6 12H2m15.657-7.657l-2.828 2.828M8.464 15.536l-2.828 2.828m12.728 0l-2.828-2.828M8.464 8.464L5.636 5.636" />
      </svg>
    </label>
  )
}

function App() {
  const apiBase = useApiBase()
  const [health, setHealth] = useState<string>('')
  const [pdfs, setPdfs] = useState<PDFDocument[]>([])
  const [currentPdf, setCurrentPdf] = useState<string>('')
  const [currentPdfName, setCurrentPdfName] = useState<string>('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [showSources, setShowSources] = useState(false)
  const [settings, setSettings] = useState<ChatSettings>({
    topK: 4,
    retrievalMode: 'similarity',
    maxTokens: 256,
    maxContextChars: 4000,
    showContext: false,
  })
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch(`${apiBase}/health`)
        const data = await res.json()
        setHealth(data.status)
      } catch {
        setHealth('unreachable')
      }
    }
    const fetchPdfs = async () => {
      try {
        const res = await fetch(`${apiBase}/pdfs`)
        const data = (await res.json()) as PDFDocument[]
        setPdfs(data)
      } catch {
        // ignore
      }
    }
    fetchHealth()
    fetchPdfs()
  }, [apiBase])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function loadPdf(pdfPath: string, pdfName: string) {
    setCurrentPdf(pdfPath)
    setCurrentPdfName(pdfName)
    setMessages([]) // Clear chat when switching documents
    try {
      await fetch(`${apiBase}/load-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pdf_path: pdfPath }),
      })
    } catch {
      // ignore
    }
  }

  async function refreshPdfs(selectPath?: string) {
    try {
      const res = await fetch(`${apiBase}/pdfs`)
      const data = (await res.json()) as PDFDocument[]
      setPdfs(data)
      if (selectPath) {
        const found = data.find((d) => d.path === selectPath)
        if (found) {
          await loadPdf(found.path, found.name)
        }
      }
    } catch {}
  }

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await fetch(`${apiBase}/upload-pdf`, { method: 'POST', body: form })
      const data = await res.json()
      if (data?.success && data?.path) {
        // If backend already selected/built index, just update current selection immediately
        setCurrentPdf(data.path)
        setCurrentPdfName(data.name || '')
        setMessages([])
        // Also refresh list to include it
        await refreshPdfs(data.path)
      }
    } catch {
    } finally {
      // reset input so same file can be selected again later
      e.target.value = ''
    }
  }

  async function sendMessage() {
    const text = input.trim()
    if (!text) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', content: text }])
    setLoading(true)
    try {
      const res = await fetch(`${apiBase}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, settings }),
      })
      const data = (await res.json()) as ChatResponse
      setMessages((m) => [...m, { role: 'assistant', content: data.answer, sources: data.sources }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: 'Error contacting server.' }])
    } finally {
      setLoading(false)
    }
  }

  function clearChat() {
    setMessages([])
  }

  return (
    <div className="min-h-screen bg-base-100 text-base-content">
      {/* Header */}
      <div className="navbar bg-base-200 border-b border-base-300">
        <div className="flex-1 px-4">
          <span className="text-2xl font-bold">💬 AI Document Chatbot</span>
          {currentPdfName && (
            <span className="ml-4 badge badge-lg badge-primary">📄 {currentPdfName}</span>
          )}
        </div>
        <div className="flex items-center gap-4 px-4">
          <span className={`badge ${health === 'healthy' ? 'badge-success' : 'badge-error'}`}>
            {health || 'checking...'}
          </span>
          <ThemeToggle />
        </div>
      </div>

      <div className="flex h-[calc(100vh-65px)]">
        {/* Left Sidebar - Document Selection & Settings */}
        <aside className="w-80 bg-base-200 border-r border-base-300 overflow-y-auto">
          <div className="p-4 space-y-4">
            {/* Document Selection */}
            <div className="card bg-base-100 shadow">
              <div className="card-body p-4">
                <h2 className="card-title text-lg">📚 Documents</h2>
                <div className="divider my-1"></div>
                <div className="mb-3">
                  <input
                    type="file"
                    accept="application/pdf"
                    className="file-input file-input-bordered file-input-sm w-full"
                    onChange={handleUpload}
                    title="Upload a PDF from your computer"
                  />
                </div>
                {!currentPdf && (
                  <div className="alert alert-warning py-2 text-sm">
                    <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                    <span>Select a document to chat</span>
                  </div>
                )}
                <ul className="menu menu-sm p-0">
                  {pdfs.map((p) => (
                    <li key={p.path}>
                      <button
                        className={currentPdf === p.path ? 'active' : ''}
                        onClick={() => loadPdf(p.path, p.name)}
                      >
                        <span className="truncate">{p.name}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Settings */}
            <div className="card bg-base-100 shadow">
              <div className="card-body p-4">
                <h2 className="card-title text-lg">⚙️ Settings</h2>
                <div className="divider my-1"></div>
                
                <label className="form-control">
                  <div className="label py-1">
                    <span className="label-text font-semibold">Top-K Context</span>
                  </div>
                  <input
                    type="range"
                    min={1}
                    max={10}
                    value={settings.topK}
                    onChange={(e) => setSettings({ ...settings, topK: Number(e.target.value) })}
                    className="range range-sm range-primary"
                  />
                  <div className="label py-0">
                    <span className="label-text-alt">{settings.topK} chunks</span>
                  </div>
                </label>

                <label className="form-control">
                  <div className="label py-1">
                    <span className="label-text font-semibold">Retrieval Mode</span>
                  </div>
                  <select
                    className="select select-bordered select-sm"
                    value={settings.retrievalMode}
                    onChange={(e) => setSettings({ ...settings, retrievalMode: e.target.value })}
                  >
                    <option value="similarity">Similarity</option>
                    <option value="mmr">MMR (Diverse)</option>
                  </select>
                </label>

                <label className="form-control">
                  <div className="label py-1">
                    <span className="label-text font-semibold">Max Tokens</span>
                  </div>
                  <input
                    type="range"
                    min={32}
                    max={2048}
                    step={32}
                    value={settings.maxTokens}
                    onChange={(e) => setSettings({ ...settings, maxTokens: Number(e.target.value) })}
                    className="range range-sm range-primary"
                  />
                  <div className="label py-0">
                    <span className="label-text-alt">{settings.maxTokens} tokens</span>
                  </div>
                </label>

                <label className="form-control">
                  <div className="label py-1">
                    <span className="label-text font-semibold">Context Size</span>
                  </div>
                  <input
                    type="range"
                    min={500}
                    max={20000}
                    step={500}
                    value={settings.maxContextChars}
                    onChange={(e) => setSettings({ ...settings, maxContextChars: Number(e.target.value) })}
                    className="range range-sm range-primary"
                  />
                  <div className="label py-0">
                    <span className="label-text-alt">{settings.maxContextChars} chars</span>
                  </div>
                </label>

                <div className="divider my-2"></div>
                
                <button onClick={clearChat} className="btn btn-outline btn-sm">
                  🗑️ Clear Chat History
                </button>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <h2 className="text-3xl font-bold mb-4">Welcome! 👋</h2>
                  <p className="text-lg opacity-70">
                    {currentPdf ? 'Ask me anything about the document!' : 'Select a document to get started'}
                  </p>
                </div>
              </div>
            )}
            {messages.map((m, idx) => (
              <div key={idx} className={`chat ${m.role === 'user' ? 'chat-end' : 'chat-start'}`}>
                <div className="chat-image avatar">
                  <div className="w-10 rounded-full bg-base-300 flex items-center justify-center">
                    {m.role === 'user' ? '👤' : '🤖'}
                  </div>
                </div>
                <div className="chat-bubble">
                  <div className="whitespace-pre-wrap">{m.content}</div>
                  {m.sources && m.sources.length > 0 && showSources && (
                    <div className="mt-2 pt-2 border-t border-base-300 opacity-70">
                      <div className="text-xs">
                        📚 Sources: {m.sources.length} chunks retrieved
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-base-300 p-4 bg-base-200">
            <div className="flex gap-2 mb-2">
              <label className="label cursor-pointer gap-2">
                <input
                  type="checkbox"
                  className="toggle toggle-sm toggle-primary"
                  checked={showSources}
                  onChange={(e) => setShowSources(e.target.checked)}
                />
                <span className="label-text">Show sources</span>
              </label>
            </div>
            <div className="flex gap-2">
              <input
                className="input input-bordered flex-1"
                placeholder={currentPdf ? "Ask something about the document..." : "Select a document first..."}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    sendMessage()
                  }
                }}
                disabled={loading || !currentPdf}
              />
              <button 
                className="btn btn-primary" 
                onClick={sendMessage} 
                disabled={loading || !currentPdf || !input.trim()}
              >
                {loading ? <span className="loading loading-spinner loading-sm" /> : '📤 Send'}
              </button>
            </div>
          </div>
        </main>

        {/* Right Sidebar - PDF Preview */}
        <aside className="w-96 bg-base-200 border-l border-base-300 overflow-hidden flex flex-col">
          <div className="p-4 border-b border-base-300">
            <h2 className="text-lg font-bold">📄 Document Preview</h2>
          </div>
          <div className="flex-1 overflow-auto p-4">
            {currentPdf ? (
              <iframe
                src={`${apiBase}/pdf-content?path=${encodeURIComponent(currentPdf)}`}
                className="w-full h-full border-2 border-base-300 rounded"
                title="PDF Preview"
              />
            ) : (
              <div className="flex items-center justify-center h-full text-center opacity-50">
                <div>
                  <p className="text-lg">No document selected</p>
                  <p className="text-sm mt-2">Select a PDF from the left panel</p>
                </div>
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  )
}

export default App
