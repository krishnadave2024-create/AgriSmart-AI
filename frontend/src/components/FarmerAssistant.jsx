import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import { Loader2, MessageSquare, Send, Info } from 'lucide-react'

const SUGGESTED = [
  { en: 'Is my crop at risk of disease?',     hi: 'क्या मेरी फसल को बीमारी का खतरा है?',        gu: 'શું મારો પાક રોગના જોખમમાં છે?' },
  { en: 'When should I irrigate next?',        hi: 'मुझे अगली बार कब सिंचाई करनी चाहिए?',        gu: 'મારે આગળ ક્યારે સિંચાઈ કરવી જોઈએ?' },
  { en: 'Which crop should I rotate to?',      hi: 'मुझे किस फसल की ओर बदलना चाहिए?',            gu: 'મારે કયા પાકમાં ફેરફાર કરવો જોઈએ?' },
  { en: 'How do I improve soil health?',       hi: 'मैं मिट्टी के स्वास्थ्य में कैसे सुधार करूं?', gu: 'હું જમીનની તંદુરસ્તી કેવી રીતે સુધારી શકું?' },
]

const LANG_NAMES = { en: 'English', hi: 'हिंदी', gu: 'ગુજરાતી' }

function FarmerAssistant() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your prototype agricultural assistant. Ask me about crop diseases, irrigation, crop recommendations, or sustainability.' }
  ])
  const [input, setInput]     = useState('')
  const [lang, setLang]       = useState('en')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const switchLang = (l) => {
    setLang(l)
    const greet = { en: 'Switched to English. How can I help you?', hi: 'हिंदी में स्विच किया गया। मैं आपकी कैसे मदद कर सकता हूँ?', gu: 'ગુજરાતીમાં સ્વિચ કર્યું. હું તમને કેવી રીતે મદદ કરી શકું?' }
    setMessages(p => [...p, { role: 'assistant', content: greet[l] }])
  }

  const send = async (msg) => {
    const text = (msg || input).trim()
    if (!text) return
    setInput('')
    setMessages(p => [...p, { role: 'user', content: text }])
    setLoading(true)
    try {
      const r = await axios.post('http://localhost:8000/api/assistant/message/', { message: text, language: lang })
      setMessages(p => [...p, { role: 'assistant', content: r.data.response, warning: r.data.warning, intent: r.data.intent }])
    } catch {
      setMessages(p => [...p, { role: 'assistant', content: "Sorry, I couldn't reach the server. Please ensure the Django API is running.", isError: true }])
    } finally { setLoading(false) }
  }

  return (
    <div className="space-y-4 flex flex-col" style={{ height: 'calc(100vh - 8rem)' }}>
      {/* Header */}
      <div className="page-header flex-shrink-0">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <MessageSquare size={26} className="text-violet-600" /> Farmer Assistant
            <span className="badge-proto ml-1 text-[10px] font-bold">PROTOTYPE</span>
          </h1>
          <p className="page-subtitle">Ask questions in English, हिंदी, or ગુજરાતી · Rule-based intent matching</p>
        </div>
        {/* Language selector */}
        <div className="flex items-center gap-2">
          {['en','hi','gu'].map((l) => (
            <button
              key={l}
              onClick={() => switchLang(l)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${lang === l ? 'bg-forest-700 text-white' : 'bg-forest-100 text-forest-600 hover:bg-forest-200'}`}
            >
              {LANG_NAMES[l]}
            </button>
          ))}
        </div>
      </div>

      {/* Prototype notice */}
      <div className="proto-banner flex-shrink-0">
        <Info size={16} className="flex-shrink-0" />
        <span>
          Prototype assistant using predefined intent-based responses.
          Responses are not AI-generated in real-time. Consult a local agricultural expert for critical decisions.
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 agri-card overflow-y-auto flex flex-col gap-3 min-h-0">
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'self-end flex flex-col items-end gap-1' : 'self-start flex flex-col items-start gap-1'}>
            {m.role === 'assistant' && (
              <div className="flex items-center gap-1.5 mb-0.5">
                <div className="w-6 h-6 rounded-full bg-forest-700 flex items-center justify-center">
                  <MessageSquare size={12} className="text-white" />
                </div>
                <span className="text-[10px] font-semibold text-forest-500">AgriSmart AI Assistant</span>
                {m.intent && m.intent !== 'unknown' && (
                  <span className="badge-green text-[9px]">{m.intent}</span>
                )}
              </div>
            )}
            <div className={m.role === 'user' ? 'bubble-user' : `bubble-bot ${m.isError ? 'border-red-200 bg-red-50 text-red-700' : ''}`}>
              {m.content}
            </div>
            {m.warning && (
              <span className="text-[10px] text-forest-400 italic max-w-[80%]">* {m.warning}</span>
            )}
          </div>
        ))}

        {loading && (
          <div className="self-start flex items-center gap-2 px-4 py-3 bg-white border border-forest-100 rounded-2xl rounded-bl-md shadow-agri">
            <Loader2 size={14} className="spin text-forest-500" />
            <span className="text-xs text-forest-500">Thinking…</span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Suggested questions */}
      <div className="flex-shrink-0 flex flex-wrap gap-2">
        {SUGGESTED.map((q, i) => (
          <button
            key={i}
            onClick={() => send(q[lang] || q.en)}
            className="text-xs px-3 py-1.5 rounded-full bg-forest-100 text-forest-700 hover:bg-forest-200 transition-colors"
            disabled={loading}
          >
            {q[lang] || q.en}
          </button>
        ))}
      </div>

      {/* Input */}
      <form
        onSubmit={(e) => { e.preventDefault(); send() }}
        className="flex-shrink-0 flex gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={lang === 'en' ? 'Ask about irrigation, disease, soil health…' : lang === 'hi' ? 'सिंचाई, रोग, मिट्टी के बारे में पूछें…' : 'સિંચાઈ, રોગ, જમીન વિશે પૂછો…'}
          className="agri-input flex-1"
          disabled={loading}
        />
        <button type="submit" className="btn-primary px-4" disabled={loading || !input.trim()} aria-label="Send message">
          <Send size={16} />
        </button>
      </form>
    </div>
  )
}

export default FarmerAssistant
