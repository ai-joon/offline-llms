import { useEffect, useMemo, useRef, useState } from 'react'
import './App.css'

type ChatSettings = {
  topK: number
  retrievalMode: string
  maxTokens: number
  maxContextChars: number
  showContext: boolean
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
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant'; content: string }[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
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

  async function loadPdf(pdfPath: string) {
    setCurrentPdf(pdfPath)
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
      setMessages((m) => [...m, { role: 'assistant', content: data.answer }])
    } catch (e) {
      setMessages((m) => [...m, { role: 'assistant', content: 'Error contacting server.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-base-100 text-base-content">
      <div className="navbar bg-base-200 border-b border-base-300">
        <div className="flex-1 px-2 text-xl font-semibold">Customer Support Chatbot</div>
        <div className="flex items-center gap-4 px-2">
          <span className="badge badge-sm " title="backend health">
            {health || '...'}
          </span>
          <ThemeToggle />
        </div>
      </div>

      <div className="container mx-auto p-4 grid grid-cols-1 lg:grid-cols-4 gap-4">
        <aside className="lg:col-span-1 space-y-4">
          <div className="card bg-base-200">
            <div className="card-body">
              <h2 className="card-title">Documents</h2>
              <ul className="menu menu-sm">
                {pdfs.map((p) => (
                  <li key={p.path}>
                    <button
                      className={currentPdf === p.path ? 'active' : ''}
                      onClick={() => loadPdf(p.path)}
                    >
                      {p.name}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="card bg-base-200">
            <div className="card-body space-y-2">
              <h2 className="card-title">Settings</h2>
              <label className="form-control">
                <div className="label"><span className="label-text">Top K</span></div>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={settings.topK}
                  onChange={(e) => setSettings({ ...settings, topK: Number(e.target.value) })}
                  className="input input-bordered"
                />
              </label>
              <label className="form-control">
                <div className="label"><span className="label-text">Max Tokens</span></div>
                <input
                  type="number"
                  min={32}
                  max={4096}
                  value={settings.maxTokens}
                  onChange={(e) => setSettings({ ...settings, maxTokens: Number(e.target.value) })}
                  className="input input-bordered"
                />
              </label>
              <label className="label cursor-pointer">
                <span className="label-text">Show Context</span>
                <input
                  type="checkbox"
                  className="toggle"
                  checked={settings.showContext}
                  onChange={(e) => setSettings({ ...settings, showContext: e.target.checked })}
                />
              </label>
            </div>
          </div>
        </aside>

        <main className="lg:col-span-3">
          <div className="card bg-base-200 h-[75vh]">
            <div className="card-body p-0 h-full flex flex-col">
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((m, idx) => (
                  <div key={idx} className={`chat ${m.role === 'user' ? 'chat-end' : 'chat-start'}`}>
                    <div className="chat-bubble whitespace-pre-wrap">
                      {m.content}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
              <div className="border-t border-base-300 p-3">
                <div className="join w-full">
                  <input
                    className="input input-bordered join-item w-full"
                    placeholder="Ask something about the documents..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') sendMessage()
                    }}
                    disabled={loading}
                  />
                  <button className="btn btn-primary join-item" onClick={sendMessage} disabled={loading}>
                    {loading ? <span className="loading loading-spinner loading-sm" /> : 'Send'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
