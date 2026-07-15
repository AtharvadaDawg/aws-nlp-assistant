const API_BASE = 'http://localhost:8002/api'

export const chatAPI = async (message, sessionId, history = []) => {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId, history }),
  })

  if (!response.ok) {
    throw new Error('Chat API error')
  }

  return response.json()
}

export const confirmAPI = async (sessionId, confirmed = true, useRealAws = true) => {
  const response = await fetch(`${API_BASE}/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      confirmed,
      use_real_aws: useRealAws,
    }),
  })

  if (!response.ok) {
    throw new Error('Confirm API error')
  }

  return response.json()
}

export const listSkills = async () => {
  const response = await fetch(`${API_BASE}/skills`)
  if (!response.ok) throw new Error('Skills API error')
  return response.json()
}

export const healthCheck = async () => {
  const response = await fetch(`${API_BASE}/health`)
  if (!response.ok) throw new Error('Health check failed')
  return response.json()
}
