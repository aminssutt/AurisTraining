import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import './ProcessingPage.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

function ProcessingPage() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_URL}/session/${sessionId}/status`)
        const data = await res.json()
        
        if (!data.success) {
          setError(data.error)
          return
        }
        
        setSession(data.session)
        
        // Si prêt, rediriger vers le chat
        if (data.session.status === 'ready') {
          setTimeout(() => {
            navigate(`/chat/${sessionId}`)
          }, 1000)
        }
        
        // Si erreur, arrêter le polling
        if (data.session.status === 'error') {
          setError(data.session.error || 'Une erreur est survenue')
          return
        }
        
      } catch (err) {
        setError('Impossible de contacter le serveur')
      }
    }

    // Vérifier le statut immédiatement
    checkStatus()
    
    // Puis toutes les secondes
    const interval = setInterval(checkStatus, 1000)
    
    return () => clearInterval(interval)
  }, [sessionId, navigate])

  const getStepIcon = (step) => {
    const icons = {
      'initialization': '🔧',
      'listing': '📋',
      'extraction': '📖',
      'extraction_complete': '✅',
      'chunking': '✂️',
      'chunking_complete': '✅',
      'indexing': '🧠',
      'complete': '🎉'
    }
    return icons[step] || '⏳'
  }

  const getStepName = (step) => {
    const names = {
      'initialization': 'Initialisation',
      'listing': 'Analyse des fichiers',
      'extraction': 'Extraction du texte',
      'extraction_complete': 'Extraction terminée',
      'chunking': 'Découpage du texte',
      'chunking_complete': 'Découpage terminé',
      'indexing': 'Indexation (IA)',
      'complete': 'Terminé !'
    }
    return names[step] || step
  }

  if (error) {
    return (
      <div className="processing-page">
        <div className="processing-container error-state">
          <div className="error-icon">❌</div>
          <h2>Erreur</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/')} className="back-button">
            ← Retour à l'accueil
          </button>
        </div>
      </div>
    )
  }

  if (!session) {
    return (
      <div className="processing-page">
        <div className="processing-container">
          <div className="loading-spinner"></div>
          <p>Chargement...</p>
        </div>
      </div>
    )
  }

  const isReady = session.status === 'ready'

  return (
    <div className="processing-page">
      <div className="processing-container">
        <div className="vehicle-badge">
          🚗 {session.vehicle_name}
        </div>

        <div className="progress-section">
          <div className="progress-header">
            <span className="step-icon">{getStepIcon(session.current_step)}</span>
            <h2>{isReady ? 'Votre assistant est prêt !' : 'Préparation en cours...'}</h2>
          </div>

          <div className="progress-bar-container">
            <div 
              className="progress-bar"
              style={{ width: `${session.progress}%` }}
            ></div>
          </div>

          <div className="progress-info">
            <span className="progress-percent">{session.progress}%</span>
            <span className="progress-message">{session.message}</span>
          </div>

          {session.total_pages > 0 && (
            <div className="pages-info">
              📄 {session.processed_pages} / {session.total_pages} pages traitées
            </div>
          )}
        </div>

        <div className="steps-timeline">
          <div className={`step ${session.progress >= 10 ? 'done' : session.progress > 0 ? 'active' : ''}`}>
            <div className="step-dot"></div>
            <span>Initialisation</span>
          </div>
          <div className={`step ${session.progress >= 50 ? 'done' : session.progress > 10 ? 'active' : ''}`}>
            <div className="step-dot"></div>
            <span>Extraction</span>
          </div>
          <div className={`step ${session.progress >= 70 ? 'done' : session.progress > 50 ? 'active' : ''}`}>
            <div className="step-dot"></div>
            <span>Découpage</span>
          </div>
          <div className={`step ${session.progress >= 95 ? 'done' : session.progress > 70 ? 'active' : ''}`}>
            <div className="step-dot"></div>
            <span>Indexation</span>
          </div>
          <div className={`step ${session.progress >= 100 ? 'done' : ''}`}>
            <div className="step-dot"></div>
            <span>Prêt</span>
          </div>
        </div>

        {isReady && (
          <button 
            className="access-button"
            onClick={() => navigate(`/chat/${sessionId}`)}
          >
            🚀 Accéder à mon chatbot
          </button>
        )}

        <div className="processing-footer">
          <p>💡 L'indexation crée une base de connaissances intelligente de vos documents</p>
        </div>
      </div>
    </div>
  )
}

export default ProcessingPage
