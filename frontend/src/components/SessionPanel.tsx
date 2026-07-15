import { Panel } from './AssistantPanel'
import type { Theme } from '../themes'

export default function SessionPanel({ theme }: { theme: Theme }) {
  const rows = [
    {
      label: 'Model',
      value: 'Gemini fallback is available when local intents do not match.',
    },
    {
      label: 'Wake Words',
      value: 'locus, local, locust, focus',
    },
    {
      label: 'Interaction',
      value: '3 sessions today · Last: 7:42 PM',
    },
    {
      label: 'Uptime',
      value: '2h 14m · CPU 1.2% · RAM 142MB',
    },
  ]

  return (
    <Panel theme={theme} title="Session Summary" action="Dashboard" actionColor={theme.accentText}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {rows.map((row, i) => (
          <div
            key={i}
            style={{
              padding: '10px 0',
              borderBottom: i < rows.length - 1 ? `1px solid ${theme.panelBorder}` : 'none',
            }}
          >
            <div style={{ fontSize: 10, fontWeight: 700, color: theme.subtext, marginBottom: 3, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
              {row.label}
            </div>
            <div style={{ fontSize: 12, color: theme.text, lineHeight: 1.5 }}>{row.value}</div>
          </div>
        ))}
      </div>
    </Panel>
  )
}
