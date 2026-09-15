import React, { useState, useRef, useEffect } from 'react'
import { Loader2, MessageSquare, Send, Info, Globe, Shield, RefreshCw } from 'lucide-react'
import api from '../utils/api'
import { useAuth } from '../context/AuthContext'

const SUGGESTED = [
  { en: 'Is my crop at risk of disease?',     hi: 'क्या मेरी फसल को बीमारी का खतरा है?',        gu: 'શું મારો પાક રોગના જોખમમાં છે?' },
  { en: 'When should I irrigate next?',        hi: 'मुझे अगली बार कब सिंचाई करनी चाहिए?',        gu: 'મારે આગળ ક્યારે સિંચાઈ કરવી જોઈએ?' },
  { en: 'Which crop should I rotate to?',      hi: 'मुझे किस फसल की ओर बदलना चाहिए?',            gu: 'મારે કયા પાકમાં ફેરફાર કરવો જોઈએ?' },
  { en: 'How do I improve soil health?',       hi: 'मैं मिट्टी के स्वास्थ्य में कैसे सुधार करूं?', gu: 'હું જમીનની તંદુરસ્તી કેવી રીતે સુધારી શકું?' },
]

const LANG_NAMES = { en: 'English', hi: 'हिंदी', gu: 'ગુજરાતી' }

function FarmerAssistant() {
  const { user } = useAuth()
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [lang, setLang] = useState('en')
  const [loading, setLoading] = useState(false)
  const [historyLoading, setHistoryLoading] = useState(true)
  const [providerStatus, setProviderStatus] = useState('checking')
  
  const endRef = useRef(null)

  useEffect(() => {
    fetchHistoryAndHealth()
  }, [])

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const fetchHistoryAndHealth = async () => {
    setHistoryLoading(true)
    try {
      const [historyRes, healthRes] = await Promise.all([
          api.get('/assistant/history/').catch(() => null),
          api.get('/assistant/health/').catch(() => null)
      ])
      
      const health = healthRes?.data
      if (health?.available) {
          setProviderStatus('live')
      } else {
          setProviderStatus('offline')
      }

      if (historyRes?.data?.success && historyRes.data.history) {
        if (historyRes.data.history.length > 0) {
            setMessages(historyRes.data.history)
        } else {
            // First time greeting
            setMessages([{ role: 'assistant', content: 'Hello! I am AgriSmart AI. I can securely access your farm profile and provide contextual agricultural advice. How can I help you today?', language: 'en' }])
        }
      }
    } catch (err) {
      console.error('Failed to fetch chat history', err)
      setMessages([{ role: 'assistant', content: 'Could not connect to backend to retrieve history.', isError: true }])
      setProviderStatus('error')
    } finally {
      setHistoryLoading(false)
    }
  }

  const switchLang = (l) => {
    setLang(l)
    const greet = { en: 'Switched to English. How can I help you?', hi: 'हिंदी में स्विच किया गया। मैं आपकी कैसे मदद कर सकता हूँ?', gu: 'ગુજરાતીમાં સ્વિચ કર્યું. હું તમને કેવી રીતે મદદ કરી શકું?' }
    setMessages(p => [...p, { role: 'assistant', content: greet[l] }])
  }

  const send = async (msgText, retryMsgObj = null) => {
    const text = (msgText || input).trim()
    if (!text || loading) return
    
    setInput('')
    
    if (retryMsgObj) {
        setMessages(p => p.filter(m => m !== retryMsgObj))
    } else {
        const newMsg = { role: 'user', content: text, language: lang }
        setMessages(p => [...p, newMsg])
    }
    
    setLoading(true)
    
    try {
      const r = await api.post('/assistant/message/', { message: text, language: lang })
      
      if (r.data.success) {
          setMessages(p => [...p, { 
              role: 'assistant', 
              content: r.data.answer, 
              source: r.data.source, 
              model_status: r.data.model_status,
              timestamp: r.data.timestamp || new Date().toISOString()
          }])
          if (r.data.model_status === 'live') setProviderStatus('live')
      } else {
          // This block might not be hit if backend returns non-200, which goes to catch
          setMessages(p => [...p, { 
              role: 'assistant', 
              content: r.data.error || "Failed to generate a response.", 
              isError: true,
              retryable: r.data.retryable || false,
              originalMessage: text
          }])
      }
    } catch (err) {
      const status = err.response?.status
      const errorData = err.response?.data || {}
      
      let errorMsg = errorData.error || "Could not reach the server. Please try again."
      let isRetryable = false
      let newProviderStatus = providerStatus

      if (status === 503) {
          errorMsg = errorData.error || "Farmer Assistant is temporarily unavailable because its AI service is not configured. Please check the backend AI settings."
          newProviderStatus = 'offline'
      } else if (status === 504) {
          errorMsg = "The response is taking too long. Please try again."
          isRetryable = true
      } else if (status === 429) {
          errorMsg = "The AI service is temporarily busy. Please try again shortly."
          isRetryable = true
      } else if (status === 502) {
          errorMsg = errorData.error || "The configured AI model is unavailable. Please check the provider and model configuration."
          newProviderStatus = 'offline'
      } else if (status === 400 || status === 401 || status === 403) {
          errorMsg = errorData.error || "Invalid request or authentication error."
      } else if (status >= 500) {
          errorMsg = errorData.error || "An unexpected server error occurred."
      } else if (!err.response) {
          errorMsg = "Network error. Please check your connection."
          isRetryable = true
      }

      setMessages(p => [...p, { 
          role: 'assistant', 
          content: errorMsg, 
          isError: true,
          retryable: isRetryable,
          originalMessage: text
      }])
      setProviderStatus(newProviderStatus)
    } finally { 
      setLoading(false) 
    }
  }

  return (
    <div className="space-y-4 flex flex-col" style={{ height: 'calc(100vh - 8rem)' }}>
      {/* Header */}
      <div className="page-header flex-shrink-0 flex justify-between items-start">
        <div>
          <h1 className="page-title flex items-center gap-2">
            <Globe size={26} className="text-violet-600" /> AgriSmart AI
            <span className={`badge ml-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${providerStatus === 'live' ? 'bg-green-100 text-green-700' : providerStatus === 'checking' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`}>
                {providerStatus === 'live' ? 'ONLINE' : providerStatus === 'checking' ? 'CHECKING...' : 'OFFLINE'}
            </span>
          </h1>
          <p className="page-subtitle">Real contextual agricultural intelligence</p>
        </div>
        {/* Language selector */}
        <div className="flex items-center gap-2">
          {['en','hi','gu'].map((l) => (
            <button
              key={l}
              onClick={() => switchLang(l)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${lang === l ? 'bg-forest-700 text-white dark:bg-forest-600' : 'bg-forest-100 text-forest-600 hover:bg-forest-200 dark:bg-forest-800 dark:text-forest-300'}`}
            >
              {LANG_NAMES[l]}
            </button>
          ))}
        </div>
      </div>

      {/* Privacy notice */}
      <div className="proto-banner flex-shrink-0">
        <Shield size={16} className="flex-shrink-0" />
        <span>
          <strong>Privacy & Safety:</strong> AgriSmart AI securely uses your authenticated records (disease scans, farm profile, irrigation advice) to provide localized guidance. It does <strong>not</strong> access live IoT/satellite data unless explicitly recorded in your history. Always verify high-impact decisions with a local agricultural expert.
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 agri-card overflow-y-auto flex flex-col gap-3 min-h-0 dark:bg-forest-900 dark:border-forest-800">
        {historyLoading ? (
             <div className="flex-1 flex justify-center items-center">
                 <Loader2 className="spin text-forest-400" size={32}/>
             </div>
        ) : messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'self-end flex flex-col items-end gap-1 max-w-[85%]' : 'self-start flex flex-col items-start gap-1 max-w-[85%]'}>
            {m.role === 'assistant' && (
              <div className="flex items-center gap-1.5 mb-0.5">
                <div className="w-6 h-6 rounded-full bg-violet-600 flex items-center justify-center">
                  <Globe size={12} className="text-white" />
                </div>
                <span className="text-[10px] font-semibold text-forest-500">AgriSmart AI</span>
                {m.source && (
                  <span className="text-[9px] bg-violet-100 text-violet-700 px-1.5 py-0.5 rounded-md font-bold uppercase">{m.source}</span>
                )}
              </div>
            )}
            
            <div className={
                m.role === 'user' 
                  ? 'bg-forest-600 text-white px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm shadow-sm' 
                  : `bg-white dark:bg-forest-950 border border-forest-100 dark:border-forest-800 text-forest-800 dark:text-forest-200 px-4 py-2.5 rounded-2xl rounded-tl-sm text-sm shadow-agri ${m.isError ? 'border-red-200 bg-red-50 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400' : ''}`
            }>
               {/* Render newlines properly */}
               {m.content.split('\n').map((line, idx) => (
                  <React.Fragment key={idx}>
                      {line}
                      {idx !== m.content.split('\n').length - 1 && <br />}
                  </React.Fragment>
               ))}
               
               {m.isError && m.retryable && (
                   <button 
                       onClick={() => send(m.originalMessage, m)}
                       className="mt-3 text-xs bg-red-600 text-white font-medium px-3 py-1.5 rounded-lg hover:bg-red-700 flex items-center gap-1.5 transition-colors"
                   >
                       <RefreshCw size={12} /> Retry
                   </button>
               )}
            </div>
            
            {m.timestamp && (
              <span className="text-[9px] text-forest-400 mt-0.5 mx-1">
                 {new Date(m.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
              </span>
            )}
          </div>
        ))}

        {loading && (
          <div className="self-start flex items-center gap-2 px-4 py-3 bg-white dark:bg-forest-950 border border-forest-100 dark:border-forest-800 rounded-2xl rounded-bl-sm shadow-agri max-w-[85%]">
            <Loader2 size={14} className="spin text-violet-500" />
            <span className="text-xs text-forest-500 font-medium tracking-wide animate-pulse">Thinking...</span>
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
            className="text-xs px-3 py-1.5 rounded-full bg-forest-100 dark:bg-forest-800 text-forest-700 dark:text-forest-300 hover:bg-forest-200 dark:hover:bg-forest-700 transition-colors disabled:opacity-50"
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
          className="agri-input flex-1 dark:bg-forest-950 dark:border-forest-700 dark:text-white disabled:opacity-50"
          disabled={loading}
          maxLength={500}
        />
        <button type="submit" className="btn-primary px-4 bg-violet-600 hover:bg-violet-700 focus:ring-violet-500 disabled:opacity-50" disabled={loading || !input.trim()} aria-label="Send message">
          <Send size={16} />
        </button>
      </form>
    </div>
  )
}

export default FarmerAssistant
