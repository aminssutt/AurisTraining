import { useState, useRef, useEffect } from 'react'
import './App.css'

// URL de l'API - utilise la variable d'environnement en production
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

// Questions suggérées
const SUGGESTIONS = [
  "Quelle est la pression recommandée pour les pneus ?",
  "Comment fonctionne le système hybride ?",
  "Que signifie le voyant moteur allumé ?",
  "Comment faire une vidange sur l'Auris ?",
  "Quelle est la capacité du coffre ?",
  "Comment activer le mode EV électrique ?",
  "Quand faut-il changer les plaquettes de frein ?",
  "Comment connecter mon téléphone en Bluetooth ?"
]

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const chatContainerRef = useRef(null)

  // Scroll automatique vers le bas
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages, isLoading])

  const sendMessage = async (messageText) => {
    const text = messageText || input.trim()
    if (!text || isLoading) return

    // Ajouter le message utilisateur
    const userMessage = { type: 'user', content: text }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text }),
      })

      const data = await response.json()

      if (data.success) {
        setMessages(prev => [...prev, { 
          type: 'bot', 
          content: data.response 
        }])
      } else {
        setMessages(prev => [...prev, { 
          type: 'error', 
          content: data.error || 'Une erreur est survenue' 
        }])
      }
    } catch (error) {
      setMessages(prev => [...prev, { 
        type: 'error', 
        content: 'Impossible de contacter le serveur. Vérifiez que le backend est lancé.' 
      }])
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

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion)
  }

  const formatMessage = (content) => {
    // Formater le markdown basique
    return content
      .split('\n')
      .map((line, i) => {
        // Gérer les listes
        if (line.startsWith('- ')) {
          return <li key={i}>{line.substring(2)}</li>
        }
        // Gérer le gras
        line = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Gérer l'italique
        line = line.replace(/\*(.*?)\*/g, '<em>$1</em>')
        return <p key={i} dangerouslySetInnerHTML={{ __html: line || '&nbsp;' }} />
      })
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1>🚗 Toyota Auris Assistant</h1>
        <p className="subtitle">Posez vos questions sur votre véhicule hybride</p>
      </header>

      {/* Questions suggérées */}
      <div className="suggestions">
        <span className="suggestions-title">💡 Questions fréquentes :</span>
        {SUGGESTIONS.map((suggestion, index) => (
          <button
            key={index}
            className="suggestion-btn"
            onClick={() => handleSuggestionClick(suggestion)}
          >
            {suggestion}
          </button>
        ))}
      </div>

      {/* Zone de chat */}
      <div className="chat-container" ref={chatContainerRef}>
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="icon">💬</div>
            <h3>Bienvenue !</h3>
            <p>Posez une question ou cliquez sur une suggestion ci-dessus</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className={`message ${message.type}`}>
              {formatMessage(message.content)}
            </div>
          ))
        )}
        
        {/* Indicateur de chargement */}
        {isLoading && (
          <div className="typing-indicator">
            <div className="dots">
              <div className="dot"></div>
              <div className="dot"></div>
              <div className="dot"></div>
            </div>
            <span className="text">L'assistant réfléchit...</span>
          </div>
        )}
      </div>

      {/* Zone de saisie */}
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Posez votre question sur la Toyota Auris..."
          disabled={isLoading}
        />
        <button 
          className="send-btn" 
          onClick={() => sendMessage()}
          disabled={!input.trim() || isLoading}
        >
          Envoyer ➤
        </button>
      </div>
    </div>
  )
}

export default App
