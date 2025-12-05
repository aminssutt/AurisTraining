import { BrowserRouter, Routes, Route } from 'react-router-dom'
import UploadPage from './pages/UploadPage'
import ProcessingPage from './pages/ProcessingPage'
import ChatPage from './pages/ChatPage'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/processing/:sessionId" element={<ProcessingPage />} />
        <Route path="/chat/:sessionId" element={<ChatPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
