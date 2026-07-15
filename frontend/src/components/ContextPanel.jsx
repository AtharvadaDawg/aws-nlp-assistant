import React from 'react'

export default function ContextPanel({ resource }) {
  if (!resource) return null

  const getAWSLink = () => {
    switch (resource.type) {
      case 'instance':
        return `https://console.aws.amazon.com/ec2/v2/home?region=${resource.region || 'ap-south-1'}#Instances:instanceId=${resource.id}`
      case 'cost':
        return 'https://console.aws.amazon.com/cost-management/home'
      case 'errors':
        return 'https://console.aws.amazon.com/cloudwatch/home'
      default:
        return 'https://console.aws.amazon.com'
    }
  }

  return (
    <div className="w-72 border-l flex flex-col p-6" style={{ borderColor: '#333333', backgroundColor: '#1a1a1a' }}>
      <h3 className="text-xs font-bold uppercase" style={{ color: '#00d9ff', letterSpacing: '0.1em' }}>
        CONTEXT
      </h3>

      <div className="mt-6 space-y-3">
        {resource.type === 'instance' && (
          <>
            <p className="text-sm font-bold" style={{ color: '#f0f0f0' }}>
              {resource.name}
            </p>
            <p className="text-xs font-medium" style={{ color: '#888888' }}>
              STATE: <span style={{ color: resource.state === 'running' ? '#39ff14' : '#ff006e', fontWeight: 'bold' }}>
                {resource.state.toUpperCase()}
              </span>
            </p>
          </>
        )}

        {resource.type === 'cost' && (
          <>
            <p className="text-lg font-bold" style={{ color: '#ffff00' }}>
              ${resource.amount?.toFixed(2)}
            </p>
            <p className="text-xs font-medium" style={{ color: '#888888' }}>
              {resource.period}
            </p>
          </>
        )}

        {resource.type === 'errors' && (
          <>
            <p className="text-sm font-bold" style={{ color: '#ff006e' }}>
              {resource.count} ERRORS
            </p>
            <p className="text-xs font-medium" style={{ color: '#888888' }}>
              Last {resource.timeframe}
            </p>
          </>
        )}
      </div>

      <a
        href={getAWSLink()}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-6 text-xs font-bold px-3 py-2 transition-all tracking-wider"
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
        View in AWS →
      </a>
    </div>
  )
}
