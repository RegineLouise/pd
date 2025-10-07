import { useState } from 'react'
import Camera from './Camera'

import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <header className="app-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
        <button
          onClick={() => window.location.href = '/'}
          style={{
            background: 'none',
            border: 'none',
            color: 'white',
            fontSize: '2rem',
            fontWeight: 'bold',
            cursor: 'pointer',
            padding: 0,
            marginLeft: '1rem',
            textShadow: '0 2px 8px rgba(0,0,0,0.2)'
          }}
        >
          MycoSCAN
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={() => window.location.href = '/history'}
            style={{
              background: 'none',
              border: 'none',
              color: 'white',
              fontSize: '1.25rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              padding: 0,
              textShadow: '0 2px 8px rgba(0,0,0,0.2)'
            }}
          >
            History
          </button>
          <button
            onClick={() => window.location.href = '/about'}
            style={{
              background: 'none',
              border: 'none',
              color: 'white',
              fontSize: '1.25rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              padding: 0,
              marginRight: '1rem',
              textShadow: '0 2px 8px rgba(0,0,0,0.2)'
            }}
          >
            About
          </button>
        </div>
      </header>
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '2rem', marginTop: '4rem' }}>
        <Camera />
       <div style={{ width: '480px', height: '360px', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', background: '#fff', overflowY: 'auto', color: '#333', whiteSpace: 'pre-line', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
         {`Onychomycosis Check:\n(Positive/Negative)\n\nSeverity Level:\n(mild, moderate, severe)\n\nRecommendations:`}
       </div>
        </div>
    </>
  )
}

export default App
