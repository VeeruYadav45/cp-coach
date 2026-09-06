import { useEffect, useState } from 'react'

function App() {
  const [status, setStatus] = useState('loading...')

  useEffect(() => {
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setStatus(data.status))
      .catch(() => setStatus('backend unreachable'))
  }, [])

  return <div style={{ padding: 20 }}>Backend status: {status}</div>
}

export default App