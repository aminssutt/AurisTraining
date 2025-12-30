import { useState, useRef, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import './ChatPage.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

function ChatPage() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const chatContainerRef = useRef(null)

  // Charger les infos de session
  useEffect(() => {
    const loadSession = async () => {
      try {
        const res = await fetch(`${API_URL}/session/${sessionId}/status`)
        const data = await res.json()
        
        if (!data.success) {
          setError('Session introuvable')
          return
        }
        
        if (data.session.status !== 'ready') {
          navigate(`/processing/${sessionId}`)
          return
        }
        
        setSession(data.session)
      } catch (err) {
        setError('Impossible de charger la session')
      }
    }
    
    loadSession()
  }, [sessionId, navigate])

  // Scroll automatique
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages, isLoading])

  const sendMessage = async (messageText) => {
    const text = messageText || input.trim()
    if (!text || isLoading) return

    const userMessage = { type: 'user', content: text }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/session/${sessionId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      })

      const data = await response.json()

      if (data.success) {
        setMessages(prev => [...prev, { type: 'bot', content: data.response }])
      } else {
        setMessages(prev => [...prev, { type: 'bot', content: `❌ Erreur: ${data.error}` }])
      }
    } catch (err) {
      setMessages(prev => [...prev, { type: 'bot', content: '❌ Erreur de connexion au serveur' }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleNewSession = () => {
    if (confirm('Créer une nouvelle session ? La session actuelle sera perdue.')) {
      navigate('/')
    }
  }

  if (error) {
    return (
      <div className="chat-page">
        <div className="chat-error">
          <h2>❌ {error}</h2>
          <button onClick={() => navigate('/')}>Retour à l'accueil</button>
        </div>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="chat-page">
        <div className="chat-loading">
          <div className="spinner"></div>
          <p>Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="chat-page">
      {/* Header */}
      <header className="chat-header">
        <div className="header-left">
          <span className="header-icon">🚗</span>
          <div className="header-info">
            <h1>Assistant {session.vehicle_name}</h1>
            <span className="header-status">
              <span className="status-dot"></span>
              En ligne
            </span>
          </div>
        </div>
        <button className="new-session-btn" onClick={handleNewSession}>
          + Nouvelle session
        </button>
      </header>

      {/* Chat Container */}
      <main className="chat-main" ref={chatContainerRef}>
        {/* Message de bienvenue */}
        {messages.length === 0 && (
          <div className="welcome-section">
            <div className="welcome-icon">🤖</div>
            <h2>Bienvenue !</h2>
            <p>
              Je suis votre assistant dédié pour le <strong>{session.vehicle_name}</strong>.
              <br />
              Posez-moi vos questions sur l'entretien, le fonctionnement ou les caractéristiques de votre véhicule.
            </p>
          </div>
        )}

        {/* Messages */}
        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              <div className="message-avatar">
                {message.type === 'user' ? '👤' : '🤖'}
              </div>
              <div className="message-content">
                {message.content}
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="message bot">
              <div className="message-avatar">🤖</div>
              <div className="message-content typing">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Input */}
      <footer className="chat-footer">
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Posez votre question sur ${session.vehicle_name}...`}
            disabled={isLoading}
          />
          <button 
            className="send-btn"
            onClick={() => sendMessage()}
            disabled={!input.trim() || isLoading}
          >
            ➤
          </button>
        </div>
        <p className="footer-hint">
          💡 Appuyez sur Entrée pour envoyer
        </p>
      </footer>
    </div>
  )
}

export default ChatPage
