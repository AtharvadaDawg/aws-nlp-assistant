import React from 'react'

export default function SuggestionChips({ questions, onSelect }) {
  return (
    <div className="flex flex-col gap-3">
      {questions.map((q, idx) => (
        <button
          key={idx}
          onClick={() => onSelect(q)}
          className="text-left px-4 py-3 transition-all font-medium"
          style={{
            borderColor: '#00d9ff',
            color: '#f0f0f0',
            backgroundColor: '#0a0a0a',
            border: '2px solid #00d9ff'
          }}
          onMouseOver={(e) => (e.target.style.backgroundColor = '#00d9ff', e.target.style.color = '#0a0a0a')}
          onMouseOut={(e) => (e.target.style.backgroundColor = '#0a0a0a', e.target.style.color = '#f0f0f0')}
        >
          <p className="text-sm">{q}</p>
        </button>
      ))}
    </div>
  )
}
