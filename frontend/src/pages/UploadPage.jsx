import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import './UploadPage.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

function UploadPage() {
  const [vehicleName, setVehicleName] = useState('')
  const [files, setFiles] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState('')
  const [uploadProgress, setUploadProgress] = useState({})
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files)
    const pdfFiles = selectedFiles.filter(f => f.type === 'application/pdf')
    
    if (pdfFiles.length !== selectedFiles.length) {
      setError('Seuls les fichiers PDF sont acceptés')
    } else {
      setError('')
    }
    
    setFiles(prev => [...prev, ...pdfFiles])
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!vehicleName.trim()) {
      setError('Veuillez entrer le nom de votre véhicule')
      return
    }
    
    if (files.length === 0) {
      setError('Veuillez sélectionner au moins un fichier PDF')
      return
    }

    setIsUploading(true)
    setError('')

    try {
      // 1. Créer la session
      const sessionRes = await fetch(`${API_URL}/session/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ vehicle_name: vehicleName.trim() })
      })
      
      const sessionData = await sessionRes.json()
      if (!sessionData.success) {
        throw new Error(sessionData.error)
      }
      
      const sessionId = sessionData.session.id
      
      // 2. Upload chaque fichier
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        const formData = new FormData()
        formData.append('file', file)
        
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: 'uploading'
        }))
        
        const uploadRes = await fetch(`${API_URL}/session/${sessionId}/upload`, {
          method: 'POST',
          body: formData
        })
        
        const uploadData = await uploadRes.json()
        if (!uploadData.success) {
          throw new Error(uploadData.error)
        }
        
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: 'done'
        }))
      }
      
      // 3. Lancer le traitement
      await fetch(`${API_URL}/session/${sessionId}/process`, {
        method: 'POST'
      })
      
      // 4. Rediriger vers la page de processing
      navigate(`/processing/${sessionId}`)
      
    } catch (err) {
      setError(err.message || 'Une erreur est survenue')
      setIsUploading(false)
    }
  }

  return (
    <div className="upload-page">
      <div className="upload-container">
        <div className="upload-header">
          <div className="logo">🚗</div>
          <h1>Vehicle Assistant</h1>
          <p>Créez votre assistant personnalisé en uploadant les manuels de votre véhicule</p>
        </div>

        <form onSubmit={handleSubmit} className="upload-form">
          {/* Nom du véhicule */}
          <div className="form-group">
            <label htmlFor="vehicleName">Nom de votre véhicule</label>
            <input
              type="text"
              id="vehicleName"
              value={vehicleName}
              onChange={(e) => setVehicleName(e.target.value)}
              placeholder="Ex: Toyota Auris Hybride 2015"
              disabled={isUploading}
            />
          </div>

          {/* Zone d'upload */}
          <div className="form-group">
            <label>Manuels du véhicule (PDF)</label>
            <div 
              className="drop-zone"
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="drop-zone-content">
                <span className="drop-icon">📄</span>
                <p>Cliquez ou glissez vos fichiers PDF ici</p>
                <span className="drop-hint">Maximum 50 MB par fichier</span>
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                multiple
                onChange={handleFileSelect}
                disabled={isUploading}
                style={{ display: 'none' }}
              />
            </div>
          </div>

          {/* Liste des fichiers */}
          {files.length > 0 && (
            <div className="files-list">
              {files.map((file, index) => (
                <div key={index} className="file-item">
                  <span className="file-icon">📕</span>
                  <div className="file-info">
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">{formatFileSize(file.size)}</span>
                  </div>
                  {uploadProgress[file.name] === 'uploading' && (
                    <span className="file-status uploading">⏳</span>
                  )}
                  {uploadProgress[file.name] === 'done' && (
                    <span className="file-status done">✅</span>
                  )}
                  {!isUploading && (
                    <button 
                      type="button" 
                      className="remove-file"
                      onClick={() => removeFile(index)}
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Erreur */}
          {error && (
            <div className="error-message">
              ⚠️ {error}
            </div>
          )}

          {/* Bouton submit */}
          <button 
            type="submit" 
            className="submit-button"
            disabled={isUploading || !vehicleName.trim() || files.length === 0}
          >
            {isUploading ? (
              <>
                <span className="spinner"></span>
                Upload en cours...
              </>
            ) : (
              <>
                🚀 Créer mon assistant
              </>
            )}
          </button>
        </form>

        <div className="upload-footer">
          <p>💡 Conseil : Uploadez le manuel d'utilisation et le guide d'entretien pour de meilleurs résultats</p>
        </div>
      </div>
    </div>
  )
}

export default UploadPage
