import React from 'react'

export default function Sidebar({ onNewChat, onOpenSettings }) {
  // Mock conversation history
  const conversations = [
    { id: 1, title: 'System Status', time: 'Today' },
    { id: 2, title: 'Cost Analysis', time: 'Yesterday' },
    { id: 3, title: 'Error Investigation', time: '2 days ago' },
  ]

  return (
    <div className="w-60 flex flex-col border-r" style={{ borderColor: '#333333', backgroundColor: '#0a0a0a' }}>
      {/* Header */}
      <div className="p-6 border-b" style={{ borderColor: '#333333' }}>
        <button
          onClick={onNewChat}
          className="w-full px-4 py-3 font-bold text-sm tracking-wider transition-all"
          style={{
            backgroundColor: '#00d9ff',
            color: '#0a0a0a',
            border: '2px solid #00d9ff',
            textTransform: 'uppercase',
            letterSpacing: '0.08em'
          }}
          onMouseOver={(e) => (e.target.style.backgroundColor = '#0a0a0a', e.target.style.color = '#00d9ff')}
          onMouseOut={(e) => (e.target.style.backgroundColor = '#00d9ff', e.target.style.color = '#0a0a0a')}
        >
          + NEW CHAT
        </button>
      </div>

      {/* History */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-xs font-bold uppercase mb-4" style={{ color: '#00d9ff', letterSpacing: '0.1em' }}>
            HISTORY
          </h3>
          <div className="space-y-2">
            {conversations.map((conv) => (
              <button
                key={conv.id}
                className="w-full text-left px-3 py-2 transition-all text-sm"
                style={{
                  border: '1px solid #333333',
                  backgroundColor: '#1a1a1a',
                  color: '#f0f0f0',
                }}
                onMouseOver={(e) => (e.target.style.backgroundColor = '#00d9ff', e.target.style.color = '#0a0a0a')}
                onMouseOut={(e) => (e.target.style.backgroundColor = '#1a1a1a', e.target.style.color = '#f0f0f0')}
              >
                <p className="font-medium truncate">{conv.title}</p>
                <p className="text-xs mt-1" style={{ color: '#888888' }}>
                  {conv.time}
                </p>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t space-y-2" style={{ borderColor: '#333333' }}>
        <button
          onClick={onOpenSettings}
          className="w-full text-left px-3 py-2 text-sm transition-all"
          style={{
            backgroundColor: 'transparent',
            color: '#888888',
            border: '1px solid #333333'
          }}
          onMouseOver={(e) => (e.target.style.color = '#00d9ff', e.target.style.borderColor = '#00d9ff')}
          onMouseOut={(e) => (e.target.style.color = '#888888', e.target.style.borderColor = '#333333')}
        >
          ⚙ Settings
        </button>
        <button
          className="w-full text-left px-3 py-2 text-sm transition-all"
          style={{
            backgroundColor: 'transparent',
            color: '#888888',
            border: '1px solid #333333'
          }}
          onMouseOver={(e) => (e.target.style.color = '#00d9ff', e.target.style.borderColor = '#00d9ff')}
          onMouseOut={(e) => (e.target.style.color = '#888888', e.target.style.borderColor = '#333333')}
        >
          ? Help
        </button>
      </div>
    </div>
  )
}
