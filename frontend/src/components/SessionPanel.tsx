import { Panel } from './AssistantPanel'
import type { Theme } from '../themes'

export default function SessionPanel({ theme }: { theme: Theme }) {
  const rows = [
    {
      label: 'Model',
      value: 'Local intent model with optional Gemini fallback.',
    },
    {
      label: 'Wake Words',
      value: 'Configured in Python settings.',
    },
    {
      label: 'Interaction',
      value: 'Runtime counters are not reported by the backend yet.',
    },
    {
      label: 'System Metrics',
      value: 'CPU, RAM, and uptime are unavailable.',
    },
  ]

  return (
    <Panel theme={theme} title="Session Summary" action="Live runtime" actionColor={theme.accentText}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {rows.map((row, i) => (
          <div
            key={row.label}
            style={{
              padding: '10px 0',
              borderBottom: i < rows.length - 1 ? `1px solid ${theme.panelBorder}` : 'none',
            }}
          >
            <div style={{ fontSize: 10, fontWeight: 700, color: theme.subtext, marginBottom: 3, letterSpacing: 0, textTransform: 'uppercase' }}>
              {row.label}
            </div>
            <div style={{ fontSize: 12, color: theme.text, lineHeight: 1.5 }}>{row.value}</div>
          </div>
        ))}
      </div>
    </Panel>
  )
}
