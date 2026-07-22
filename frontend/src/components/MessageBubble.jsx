import React from 'react'
import MiniChart from './MiniChart'
import ActionProposal from './ActionProposal'

export default function MessageBubble({
  role,
  content,
  data,
  dataType,
  proposal,
  proposalResolved,
  onConfirm,
  onCancel,
  confirming,
}) {
  const isUser = role === 'user'
  const isError = role === 'error'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className="max-w-md lg:max-w-2xl px-4 py-3"
        style={
          isUser
            ? { backgroundColor: '#00d9ff', color: '#0a0a0a', border: '2px solid #00d9ff' }
            : isError
            ? { backgroundColor: '#ff006e', color: '#f0f0f0', border: '2px solid #ff006e' }
            : { backgroundColor: '#1a1a1a', color: '#f0f0f0', border: '2px solid #333333' }
        }
      >
        <p className="text-sm leading-relaxed font-medium">{content}</p>

        {proposal && (
          <ActionProposal
            proposal={proposal}
            resolved={proposalResolved}
            loading={confirming}
            onConfirm={onConfirm}
            onCancel={onCancel}
          />
        )}

        {data && dataType && !isUser && !isError && (
          <div className="mt-3 pt-3" style={{ borderTop: '2px solid #333333' }}>
            {dataType === 'instances' && (
              <div className="space-y-2">
                {data.instances?.map((inst, i) => (
                  <div key={i} className="text-xs flex items-center gap-2" style={{ color: '#f0f0f0' }}>
                    <span
                      className="w-2 h-2"
                      style={{ backgroundColor: inst.state === 'running' ? '#39ff14' : '#ff006e' }}
                    />
                    <span className="font-bold">{inst.name}</span>
                    {inst.cpu_avg != null && (
                      <span style={{ color: '#888888' }}>CPU {inst.cpu_avg}%</span>
                    )}
                  </div>
                ))}
              </div>
            )}

            {dataType === 'cost' && (
              <div className="text-xs space-y-3">
                <div>
                  <div className="font-bold text-base" style={{ color: '#ffff00' }}>
                    ${data.total_cost?.toFixed(2)}
                  </div>
                  <div style={{ color: '#888888' }}>{data.period}</div>
                </div>
                {data.chart_data?.length > 0 && (
                  <div className="mt-2 pt-2" style={{ borderTop: '1px dashed #333' }}>
                    <div className="text-[10px] font-bold uppercase mb-1" style={{ color: '#888888' }}>Cost by Service</div>
                    <MiniChart data={data.chart_data} type="bar" />
                  </div>
                )}
              </div>
            )}

            {dataType === 'metrics' && data.chart_data?.length > 0 && (
              <MiniChart data={data.chart_data} type={data.chart_type || 'line'} />
            )}

            {dataType === 'errors' && (
              <div className="text-xs space-y-1">
                <div className="font-bold text-base" style={{ color: '#ff006e' }}>
                  {data.total_errors} ERRORS
                </div>
                <div style={{ color: '#888888' }}>Last 1 hour</div>
              </div>
            )}

            {dataType === 's3' && (
              <div className="space-y-2">
                {data.buckets?.map((bucket, i) => (
                  <div key={i} className="text-xs flex items-center justify-between py-1" style={{ borderBottom: '1px solid #222' }}>
                    <div className="flex items-center gap-2">
                      <span style={{ color: '#00d9ff' }}>🪣</span>
                      <span className="font-bold" style={{ color: '#f0f0f0' }}>{bucket.name}</span>
                      <span style={{ color: '#666' }}>({bucket.region})</span>
                    </div>
                    <span
                      className="text-[10px] px-1.5 py-0.5 font-bold tracking-wider"
                      style={{
                        backgroundColor: bucket.is_public ? '#ff006e' : '#333333',
                        color: bucket.is_public ? '#f0f0f0' : '#888888'
                      }}
                    >
                      {bucket.is_public ? 'PUBLIC' : 'PRIVATE'}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {dataType === 'rds' && (
              <div className="space-y-2">
                {data.db_instances?.map((db, i) => (
                  <div key={i} className="text-xs flex items-center justify-between py-1" style={{ borderBottom: '1px solid #222' }}>
                    <div className="flex items-center gap-2">
                      <span style={{ color: '#00d9ff' }}>🗄️</span>
                      <span className="font-bold" style={{ color: '#f0f0f0' }}>{db.id}</span>
                      <span style={{ color: '#888888' }}>({db.class})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span style={{ color: '#666' }}>{db.engine}</span>
                      <span
                        className="text-[10px] px-1.5 py-0.5 font-bold tracking-wider"
                        style={{
                          backgroundColor: db.status === 'available' ? '#39ff14' : '#ffff00',
                          color: '#0a0a0a'
                        }}
                      >
                        {db.status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {dataType === 'lambda' && (
              <div className="space-y-2">
                {data.functions?.map((fn, i) => (
                  <div key={i} className="text-xs flex items-center justify-between py-1" style={{ borderBottom: '1px solid #222' }}>
                    <div className="flex items-center gap-2">
                      <span style={{ color: '#00d9ff' }}>λ</span>
                      <span className="font-bold" style={{ color: '#f0f0f0' }}>{fn.name}</span>
                      <span style={{ color: '#666' }}>({fn.runtime})</span>
                    </div>
                    <span style={{ color: '#888888' }}>{((fn.size_bytes || 0) / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                ))}
              </div>
            )}

            {dataType === 'dynamodb' && (
              <div className="space-y-2">
                {data.tables?.map((table, i) => (
                  <div key={i} className="text-xs flex items-center justify-between py-1" style={{ borderBottom: '1px solid #222' }}>
                    <div className="flex items-center gap-2">
                      <span style={{ color: '#39ff14' }}>📊</span>
                      <span className="font-bold" style={{ color: '#f0f0f0' }}>{table.name}</span>
                      <span style={{ color: '#888888' }}>({table.item_count?.toLocaleString()} items)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span style={{ color: '#666' }}>{((table.size_bytes || 0) / 1024 / 1024).toFixed(2)} MB</span>
                      <span
                        className="text-[10px] px-1.5 py-0.5 font-bold tracking-wider"
                        style={{
                          backgroundColor: table.status === 'ACTIVE' ? '#39ff14' : '#ffff00',
                          color: '#0a0a0a'
                        }}
                      >
                        {table.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {dataType === 'sqs' && (
              <div className="space-y-2">
                {data.queues?.map((queue, i) => (
                  <div key={i} className="text-xs flex items-center justify-between py-1" style={{ borderBottom: '1px solid #222' }}>
                    <div className="flex items-center gap-2">
                      <span style={{ color: '#ff006e' }}>✉️</span>
                      <span className="font-bold" style={{ color: '#f0f0f0' }}>{queue.name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span style={{ color: '#888888' }}>
                        Visible: <strong style={{ color: queue.visible_messages > 0 ? '#ff006e' : '#f0f0f0' }}>{queue.visible_messages}</strong>
                      </span>
                      <span style={{ color: '#666' }}>
                        In-flight: <strong>{queue.invisible_messages}</strong>
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {dataType === 'iam' && (
              <div className="space-y-2">
                {data.users?.map((user, i) => (
                  <div key={i} className="text-xs flex items-center justify-between py-1" style={{ borderBottom: '1px solid #222' }}>
                    <div className="flex items-center gap-2">
                      <span style={{ color: '#00d9ff' }}>👤</span>
                      <span className="font-bold" style={{ color: '#f0f0f0' }}>{user.name}</span>
                      {user.login_profile_exists && <span className="text-[9px] px-1 bg-[#222] text-[#888]">CONSOLE ACCESS</span>}
                    </div>
                    <span
                      className="text-[10px] px-1.5 py-0.5 font-bold tracking-wider"
                      style={{
                        backgroundColor: user.mfa_active ? '#39ff14' : '#ff006e',
                        color: user.mfa_active ? '#0a0a0a' : '#f0f0f0'
                      }}
                    >
                      {user.mfa_active ? 'MFA ACTIVE' : 'NO MFA'}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {dataType === 'ecs' && (
              <div className="space-y-2">
                {data.clusters?.map((cluster, i) => (
                  <div key={i} className="text-xs flex items-center justify-between py-1" style={{ borderBottom: '1px solid #222' }}>
                    <div className="flex items-center gap-2">
                      <span style={{ color: '#00d9ff' }}>🐳</span>
                      <span className="font-bold" style={{ color: '#f0f0f0' }}>{cluster.name}</span>
                      <span style={{ color: '#666' }}>({cluster.services_count} services)</span>
                    </div>
                    <span
                      className="text-[10px] px-1.5 py-0.5 font-bold tracking-wider"
                      style={{
                        backgroundColor: '#333333',
                        color: '#39ff14'
                      }}
                    >
                      {cluster.running_tasks} RUNNING TASKS
                    </span>
                  </div>
                ))}
              </div>
            )}

            {dataType === 'savings' && (
              <div className="space-y-3">
                <div className="text-xs font-bold uppercase tracking-wider mb-2" style={{ color: '#39ff14' }}>
                  Total Estimated Savings: ${data.total_est_savings?.toFixed(2)}/mo
                </div>

                {data.stopped_instances?.length > 0 && (
                  <div>
                    <div className="text-[10px] font-bold uppercase mb-1" style={{ color: '#888888' }}>Stopped EC2 Instances (Billing for EBS storage only)</div>
                    {data.stopped_instances.map((inst, i) => (
                      <div key={i} className="text-xs flex justify-between py-0.5" style={{ color: '#f0f0f0' }}>
                        <span>🖥️ {inst.name} ({inst.type})</span>
                        <span style={{ color: '#ffff00' }}>Save ~${inst.cost_est_savings}/mo</span>
                      </div>
                    ))}
                  </div>
                )}

                {data.unattached_volumes?.length > 0 && (
                  <div>
                    <div className="text-[10px] font-bold uppercase mb-1" style={{ color: '#888888' }}>Unattached EBS Volumes (Idle storage costing money)</div>
                    {data.unattached_volumes.map((vol, i) => (
                      <div key={i} className="text-xs flex justify-between py-0.5" style={{ color: '#f0f0f0' }}>
                        <span>💾 {vol.id} ({vol.size_gb} GB {vol.type})</span>
                        <span style={{ color: '#ffff00' }}>Save ${vol.cost_est_savings}/mo</span>
                      </div>
                    ))}
                  </div>
                )}

                {(!data.stopped_instances?.length && !data.unattached_volumes?.length) && (
                  <div className="text-xs font-medium" style={{ color: '#888888' }}>
                    No idle resources found! Your cloud usage is fully optimized.
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
