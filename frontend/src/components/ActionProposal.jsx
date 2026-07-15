import React from 'react'

const RISK_STYLES = {
  none: { bg: '#00d9ff', color: '#0a0a0a', label: 'NO RISK' },
  low: { bg: '#39ff14', color: '#0a0a0a', label: 'LOW RISK' },
  medium: { bg: '#ffff00', color: '#0a0a0a', label: 'MEDIUM RISK' },
  high: { bg: '#ff006e', color: '#f0f0f0', label: 'HIGH RISK' },
}

export default function ActionProposal({ proposal, resolved, onConfirm, onCancel, loading }) {
  const risk = RISK_STYLES[proposal?.risk] || RISK_STYLES.medium

  return (
    <div
      className="mt-3 pt-3 space-y-4"
      style={{ borderTop: '2px solid #333333' }}
    >
      <div>
        <p className="text-sm font-bold" style={{ color: '#f0f0f0' }}>
          {proposal?.title}
        </p>
        <p className="text-xs mt-2 leading-relaxed" style={{ color: '#888888' }}>
          {proposal?.description}
        </p>
      </div>

      <div className="flex items-center gap-2">
        <span
          className="text-xs px-2 py-1 font-bold tracking-wider"
          style={{ backgroundColor: risk.bg, color: risk.color }}
        >
          {risk.label}
        </span>
        <span className="text-xs font-medium" style={{ color: '#888888' }}>
          {proposal?.mode} MODE
        </span>
      </div>

      {!resolved && (
        <div className="flex gap-3">
          <button
            onClick={onConfirm}
            disabled={loading}
            className="px-4 py-2 text-xs font-bold tracking-wider disabled:opacity-40"
            style={{
              backgroundColor: '#39ff14',
              color: '#0a0a0a',
              border: '2px solid #39ff14',
              textTransform: 'uppercase',
            }}
          >
            {loading ? 'RUNNING...' : 'CONFIRM'}
          </button>
          <button
            onClick={onCancel}
            disabled={loading}
            className="px-4 py-2 text-xs font-bold tracking-wider disabled:opacity-40"
            style={{
              backgroundColor: 'transparent',
              color: '#888888',
              border: '2px solid #333333',
              textTransform: 'uppercase',
            }}
          >
            CANCEL
          </button>
        </div>
      )}
    </div>
  )
}
