import React from 'react'

const SKILL_LABELS = {
  system_health: '🖥️ SYSTEM HEALTH',
  recent_errors: '🔴 ERROR LOGS',
  cloud_cost: '💰 COST DATA',
  recent_changes: '📋 CLOUDTRAIL',
  service_metrics: '📊 METRICS',
  s3_status: '🪣 S3 AUDIT',
  rds_status: '🗄️ RDS DB STATUS',
  cost_optimization: '💸 COST SAVINGS',
  action_restart: '↻ RESTART',
  action_stop: '⏹ STOP',
  action_scale: '⬆ SCALE',
  action_alarm: '🔔 ALARM',
  action_postmortem: '📝 POSTMORTEM',
  action_create_instance: '🚀 CREATE INSTANCE',
  action_create_s3_bucket: '🪣 CREATE BUCKET',
  action_rds_snapshot: '📸 DB SNAPSHOT',
  unknown: '🤔 PROCESSING',
}

export default function ThinkingStep({ skill, thinking }) {
  const label = SKILL_LABELS[skill] || SKILL_LABELS.unknown

  return (
    <div className="flex items-start gap-2 mb-4 animate-fade-in" style={{ animationDuration: '0.3s' }}>
      <div
        className="text-xs px-3 py-1.5 font-bold tracking-wider"
        style={{
          backgroundColor: '#00d9ff',
          color: '#0a0a0a',
          border: '2px solid #00d9ff',
        }}
      >
        {label}
      </div>
      {thinking && (
        <div className="text-xs px-3 py-1.5 font-medium" style={{ color: '#888888', letterSpacing: '0.05em' }}>
          {thinking}
        </div>
      )}
    </div>
  )
}
