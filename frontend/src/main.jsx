import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import SmoothScroll from './components/SmoothScroll.jsx'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <SmoothScroll>
      <App />
    </SmoothScroll>
  </StrictMode>,
)
