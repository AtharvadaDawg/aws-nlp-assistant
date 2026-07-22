const API_BASE = 'http://localhost:8002/api'

const getAwsHeaders = () => {
  const headers = { 'Content-Type': 'application/json' }
  const accessKey = localStorage.getItem('aws_access_key_id')
  const secretKey = localStorage.getItem('aws_secret_access_key')
  const region = localStorage.getItem('aws_region')

  if (accessKey) headers['X-AWS-Access-Key-Id'] = accessKey
  if (secretKey) headers['X-AWS-Secret-Access-Key'] = secretKey
  if (region) headers['X-AWS-Region'] = region

  return headers
}

export const chatAPI = async (message, sessionId, history = []) => {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: getAwsHeaders(),
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
    headers: getAwsHeaders(),
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
