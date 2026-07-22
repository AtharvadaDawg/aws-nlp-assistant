import React, { useState, useEffect, useRef } from 'react'
import Sidebar from '../components/Sidebar'
import MessageBubble from '../components/MessageBubble'
import ThinkingStep from '../components/ThinkingStep'
import ContextPanel from '../components/ContextPanel'
import SuggestionChips from '../components/SuggestionChips'
import { chatAPI, confirmAPI } from '../utils/api'

const SUGGESTED_QUESTIONS = [
  'Is our system running fine right now?',
  'What broke last Tuesday night?',
  'How much did we spend on cloud this month?',
  'Which service had the most errors this week?',
  'What changed in our infrastructure recently?',
]

function generateUUID() {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

function newSessionId() {
  return generateUUID()
}

function applyContextFromResponse(response, setContextResource) {
  if (response.data_type === 'instances' && response.data?.instances?.length > 0) {
    const inst = response.data.instances[0]
    setContextResource({
      type: 'instance',
      name: inst.name || inst.id,
      id: inst.id,
      state: inst.state,
      region: inst.region || 'ap-south-1',
    })
  } else if (response.data_type === 'cost' && response.data?.period) {
    setContextResource({
      type: 'cost',
      period: response.data.period,
      amount: response.data.total_cost,
    })
  } else if (response.data_type === 'errors' && response.data?.total_errors != null) {
    setContextResource({
      type: 'errors',
      count: response.data.total_errors,
      timeframe: '1 hour',
    })
  }
}

export default function ChatPage() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [confirmingId, setConfirmingId] = useState(null)
  const [sessionId, setSessionId] = useState(newSessionId)
  const [contextResource, setContextResource] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  const [isSettingsOpen, setIsSettingsOpen] = useState(false)
  const [awsAccessKey, setAwsAccessKey] = useState('')
  const [awsSecretKey, setAwsSecretKey] = useState('')
  const [awsRegion, setAwsRegion] = useState('ap-south-1')

  useEffect(() => {
    const key = localStorage.getItem('aws_access_key_id') || ''
    const secret = localStorage.getItem('aws_secret_access_key') || ''
    const reg = localStorage.getItem('aws_region') || 'ap-south-1'
    setAwsAccessKey(key)
    setAwsSecretKey(secret)
    setAwsRegion(reg)
  }, [isSettingsOpen])

  const handleSaveSettings = () => {
    localStorage.setItem('aws_access_key_id', awsAccessKey.trim())
    localStorage.setItem('aws_secret_access_key', awsSecretKey.trim())
    localStorage.setItem('aws_region', awsRegion.trim())
    setIsSettingsOpen(false)
  }

  const handleClearSettings = () => {
    localStorage.removeItem('aws_access_key_id')
    localStorage.removeItem('aws_secret_access_key')
    localStorage.removeItem('aws_region')
    setAwsAccessKey('')
    setAwsSecretKey('')
    setAwsRegion('ap-south-1')
    setIsSettingsOpen(false)
  }

  useEffect(() => {
    const initParticles = () => {
      if (window.particlesJS) {
        window.particlesJS('particles-js', {
          "particles": {
            "number": {
              "value": 160,
              "density": {
                "enable": true,
                "value_area": 400
              }
            },
            "color": {
              "value": "#00d9ff"
            },
            "shape": {
              "type": "circle"
            },
            "opacity": {
              "value": 0.5,
              "random": false
            },
            "size": {
              "value": 2.0,
              "random": true
            },
            "line_linked": {
              "enable": true,
              "distance": 150,
              "color": "#00d9ff",
              "opacity": 0.35,
              "width": 1
            },
            "move": {
              "enable": true,
              "speed": 1.6,
              "direction": "none",
              "random": false,
              "straight": false,
              "out_mode": "out",
              "bounce": false
            },
            "interactivity": {

            }
          },
          "retina_detect": true
        });
        return true;
      }
      return false;
    };

    if (!initParticles()) {
      let attempts = 0;
      const interval = setInterval(() => {
        attempts++;
        if (initParticles() || attempts > 20) {
          clearInterval(interval);
        }
      }, 150);
      return () => clearInterval(interval);
    }
  }, []);

  const hasPendingAction = messages.some(
    (m) => m.type === 'action_proposal' && !m.resolved
  )

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading, confirmingId])

  const handleSuggestedQuestion = (question) => {
    setInput(question)
    setTimeout(() => inputRef.current?.focus(), 0)
  }

  const handleSend = async () => {
    if (!input.trim() || loading || hasPendingAction) return

    const userMessage = input.trim()
    setInput('')

    const history = messages
      .filter((m) => m.role === 'user' || m.role === 'assistant')
      .map((m) => ({
        role: m.role,
        content: m.content,
      }))

    setMessages((prev) => [...prev, { id: generateUUID(), role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await chatAPI(userMessage, sessionId, history)

      if (response.type === 'action_proposal') {
        setMessages((prev) => [
          ...prev,
          {
            id: generateUUID(),
            role: 'assistant',
            type: 'action_proposal',
            content: response.answer,
            thinking: response.thinking,
            skillUsed: response.skill_used,
            proposal: response.proposal,
            resolved: false,
          },
        ])
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: generateUUID(),
            role: 'assistant',
            content: response.answer,
            thinking: response.thinking,
            skillUsed: response.skill_used,
            dataType: response.data_type,
            data: response.data,
            confidence: response.confidence,
          },
        ])
        applyContextFromResponse(response, setContextResource)
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: generateUUID(), role: 'error', content: 'Sorry, something went wrong. Please try again.' },
      ])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  const handleConfirmAction = async (messageId) => {
    setConfirmingId(messageId)
    try {
      const result = await confirmAPI(sessionId, true)
      setMessages((prev) =>
        prev.map((m) => (m.id === messageId ? { ...m, resolved: true } : m))
      )
      setMessages((prev) => [
        ...prev,
        {
          id: generateUUID(),
          role: 'assistant',
          content: result.message || (result.success ? 'Action completed.' : 'Action failed.'),
          skillUsed: result.action,
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: generateUUID(), role: 'error', content: 'Failed to execute action. Please try again.' },
      ])
    } finally {
      setConfirmingId(null)
    }
  }

  const handleCancelAction = async (messageId) => {
    setConfirmingId(messageId)
    try {
      const result = await confirmAPI(sessionId, false)
      setMessages((prev) =>
        prev.map((m) => (m.id === messageId ? { ...m, resolved: true } : m))
      )
      setMessages((prev) => [
        ...prev,
        {
          id: generateUUID(),
          role: 'assistant',
          content: result.message || 'Action cancelled. Nothing was changed.',
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        { id: generateUUID(), role: 'error', content: 'Failed to cancel action. Please try again.' },
      ])
    } finally {
      setConfirmingId(null)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleNewChat = () => {
    setMessages([])
    setInput('')
    setContextResource(null)
    setSessionId(newSessionId())
    inputRef.current?.focus()
  }

  const isEmpty = messages.length === 0

  return (
    <div className="flex h-screen overflow-hidden relative" style={{ backgroundColor: '#0a0a0a' }}>
      <div id="particles-js" style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', zIndex: 0, pointerEvents: 'none' }} />

      <Sidebar onNewChat={handleNewChat} onOpenSettings={() => setIsSettingsOpen(true)} />

      <div className="flex-1 flex flex-col relative z-10" style={{ backgroundColor: 'transparent' }}>
        <div className="flex-1 overflow-y-auto px-8 py-8 space-y-6">
          {isEmpty ? (
            <div className="h-full flex flex-col items-center justify-center">
              <div className="max-w-md text-center space-y-8">
                <h1
                  className="text-4xl font-bold tracking-tighter"
                  style={{ color: '#f0f0f0', letterSpacing: '-0.03em' }}
                >
                  ASK YOUR INFRASTRUCTURE
                </h1>
                <p
                  className="text-base font-medium"
                  style={{ color: '#888888', letterSpacing: '0.05em', textTransform: 'uppercase' }}
                >
                  Try one of these or ask your own:
                </p>
              </div>
              <div className="mt-12 w-full max-w-2xl">
                <SuggestionChips questions={SUGGESTED_QUESTIONS} onSelect={handleSuggestedQuestion} />
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg) => (
                <div key={msg.id}>
                  {msg.thinking && msg.role === 'assistant' && (
                    <ThinkingStep skill={msg.skillUsed} thinking={msg.thinking} />
                  )}
                  <MessageBubble
                    role={msg.role}
                    content={msg.content}
                    data={msg.data}
                    dataType={msg.dataType}
                    proposal={msg.type === 'action_proposal' ? msg.proposal : null}
                    proposalResolved={msg.resolved}
                    confirming={confirmingId === msg.id}
                    onConfirm={msg.type === 'action_proposal' ? () => handleConfirmAction(msg.id) : undefined}
                    onCancel={msg.type === 'action_proposal' ? () => handleCancelAction(msg.id) : undefined}
                  />
                </div>
              ))}
              {loading && (
                <ThinkingStep skill="unknown" thinking="Processing your question..." />
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div
          style={{ borderTopColor: '#333333', backgroundColor: '#0a0a0a' }}
          className="border-t px-8 py-6"
        >
          {hasPendingAction && (
            <p className="text-xs font-medium mb-3 text-center" style={{ color: '#ffff00' }}>
              Confirm or cancel the pending action before sending another message.
            </p>
          )}
          <div className="flex gap-3 items-end max-w-5xl mx-auto">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                hasPendingAction
                  ? 'Resolve the pending action first...'
                  : 'Ask me about your AWS infrastructure...'
              }
              disabled={loading || hasPendingAction}
              className="flex-1 px-4 py-3 text-sm font-medium focus:outline-none disabled:opacity-50"
              style={{
                backgroundColor: '#1a1a1a',
                color: '#f0f0f0',
                borderColor: '#333333',
                border: '2px solid #333333',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#00d9ff'
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#333333'
              }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading || hasPendingAction}
              className="px-6 py-3 font-bold text-sm tracking-wider disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              style={{
                backgroundColor: '#00d9ff',
                color: '#0a0a0a',
                border: '2px solid #00d9ff',
                textTransform: 'uppercase',
                letterSpacing: '0.1em',
              }}
              onMouseOver={(e) => {
                if (!loading && input.trim() && !hasPendingAction) {
                  e.target.style.backgroundColor = '#0a0a0a'
                  e.target.style.color = '#00d9ff'
                }
              }}
              onMouseOut={(e) => {
                e.target.style.backgroundColor = '#00d9ff'
                e.target.style.color = '#0a0a0a'
              }}
            >
              {loading ? 'SENDING' : 'SEND'}
            </button>
          </div>
        </div>
      </div>

      {contextResource && <ContextPanel resource={contextResource} />}

      {isSettingsOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm">
          <div className="max-w-md w-full p-6 space-y-6 border" style={{ backgroundColor: '#0a0a0a', borderColor: '#333333' }}>
            <div className="space-y-1">
              <h2 className="text-xl font-bold tracking-tight" style={{ color: '#00d9ff' }}>
                AWS CREDENTIALS
              </h2>
              <p className="text-xs" style={{ color: '#888888' }}>
                Configure session-based credentials for your live AWS account. These are stored locally in your browser.
              </p>
            </div>

            <div className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider" style={{ color: '#f0f0f0' }}>Access Key ID</label>
                <input
                  type="text"
                  value={awsAccessKey}
                  onChange={(e) => setAwsAccessKey(e.target.value)}
                  placeholder="AKIA..."
                  className="w-full px-3 py-2 text-sm font-medium focus:outline-none"
                  style={{ backgroundColor: '#1a1a1a', color: '#f0f0f0', border: '1px solid #333333' }}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider" style={{ color: '#f0f0f0' }}>Secret Access Key</label>
                <input
                  type="password"
                  value={awsSecretKey}
                  onChange={(e) => setAwsSecretKey(e.target.value)}
                  placeholder="••••••••••••••••"
                  className="w-full px-3 py-2 text-sm font-medium focus:outline-none"
                  style={{ backgroundColor: '#1a1a1a', color: '#f0f0f0', border: '1px solid #333333' }}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold uppercase tracking-wider" style={{ color: '#f0f0f0' }}>Default Region</label>
                <input
                  type="text"
                  value={awsRegion}
                  onChange={(e) => setAwsRegion(e.target.value)}
                  placeholder="ap-south-1"
                  className="w-full px-3 py-2 text-sm font-medium focus:outline-none"
                  style={{ backgroundColor: '#1a1a1a', color: '#f0f0f0', border: '1px solid #333333' }}
                />
              </div>
            </div>

            <div className="flex flex-col gap-2 pt-2">
              <button
                onClick={handleSaveSettings}
                className="w-full py-2.5 font-bold text-xs tracking-wider transition-all"
                style={{ backgroundColor: '#00d9ff', color: '#0a0a0a', border: '1px solid #00d9ff', textTransform: 'uppercase' }}
              >
                Save & Connect
              </button>
              <div className="flex gap-2">
                <button
                  onClick={handleClearSettings}
                  className="flex-1 py-2 font-bold text-xs tracking-wider transition-all"
                  style={{ backgroundColor: 'transparent', color: '#ff006e', border: '1px solid #ff006e', textTransform: 'uppercase' }}
                >
                  Clear Keys
                </button>
                <button
                  onClick={() => setIsSettingsOpen(false)}
                  className="flex-1 py-2 font-bold text-xs tracking-wider transition-all"
                  style={{ backgroundColor: 'transparent', color: '#888888', border: '1px solid #333333', textTransform: 'uppercase' }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
