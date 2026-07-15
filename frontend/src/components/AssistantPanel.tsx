import type { Theme } from '../themes'
import type { AppStatus } from '../App'

const catMessages: Record<AppStatus, string> = {
  idle: 'Go ahead',
  listening: 'Listening...',
  thinking: '...',
  speaking: 'Say that again!',
}

const nyanMessages: Record<AppStatus, string> = {
  idle: 'can i haz?',
  listening: 'im listenin',
  thinking: 'big thonk...',
  speaking: 'meow meow',
}

export default function AssistantPanel({
  theme,
  status,
  onListen,
}: {
  theme: Theme
  status: AppStatus
  onListen: () => void
}) {
  const isNyan = theme.name === 'cat'
  const overlayText = isNyan ? nyanMessages[status] : catMessages[status]

  return (
    <Panel theme={theme} title={isNyan ? '\u{1F431} Assistant' : 'Assistant'} action="Click the cat to wake it">
      <div style={{ display: 'flex', gap: 16, height: '100%' }}>
        {/* Cat image area */}
        <div
          onClick={onListen}
          style={{
            width: 140,
            flexShrink: 0,
            borderRadius: 10,
            overflow: 'hidden',
            cursor: 'pointer',
            position: 'relative',
            background: '#0a1a0c',
          }}
        >
          <img
            src="https://images.unsplash.com/photo-1574158622682-e40e69881006?w=280&h=280&fit=crop&auto=format"
            alt="Assistant cat"
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block', opacity: 0.9 }}
          />
          {/* Overlay label */}
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              padding: '20px 10px 10px',
              background: 'linear-gradient(transparent, rgba(0,0,0,0.7))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <span
              style={{
                color: theme.accent,
                fontWeight: 800,
                fontSize: 14,
                textShadow: `0 0 12px ${theme.accent}`,
                letterSpacing: '0.02em',
              }}
            >
              {overlayText}
            </span>
          </div>
        </div>

        {/* Control deck */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: theme.text, marginBottom: 2 }}>Control Deck</p>
            <p style={{ fontSize: 11, color: theme.subtext, lineHeight: 1.4 }}>
              Manual wake, visual status, and wake-word cues live here.
            </p>
          </div>

          <button
            onClick={onListen}
            style={{
              background: status === 'idle' ? theme.listenBtn : `${theme.accent}44`,
              color: status === 'idle' ? theme.listenBtnText : theme.accentText,
              border: `1px solid ${theme.accent}`,
              borderRadius: 8,
              padding: '10px 0',
              fontWeight: 700,
              fontSize: 13,
              cursor: 'pointer',
              letterSpacing: '0.04em',
              transition: 'all 0.25s ease',
              boxShadow: status === 'idle' ? `0 0 16px ${theme.accent}44` : 'none',
            }}
          >
            {status === 'idle' ? 'Listen' : 'Stop'}
          </button>

          <button
            style={{
              background: theme.inputBg,
              color: theme.subtext,
              border: `1px solid ${theme.panelBorder}`,
              borderRadius: 8,
              padding: '9px 0',
              fontWeight: 500,
              fontSize: 13,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            Settings
          </button>

          <div style={{ marginTop: 'auto', display: 'flex', alignItems: 'center', gap: 6 }}>
            <div
              style={{
                width: 7,
                height: 7,
                borderRadius: '50%',
                background: theme.accent,
                boxShadow: `0 0 8px ${theme.accent}`,
              }}
            />
            <span style={{ fontSize: 11, color: theme.accentText, fontWeight: 500 }}>
              Wake Word Ready
            </span>
          </div>
        </div>
      </div>
    </Panel>
  )
}

export function Panel({
  theme,
  title,
  action,
  actionColor,
  children,
}: {
  theme: Theme
  title: string
  action?: string
  actionColor?: string
  children: React.ReactNode
}) {
  return (
    <div
      style={{
        background: theme.panelBg,
        border: `1px solid ${theme.panelBorder}`,
        borderRadius: 14,
        padding: '14px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
        backdropFilter: 'blur(20px) saturate(1.4)',
        WebkitBackdropFilter: 'blur(20px) saturate(1.4)',
        transition: 'background 0.3s ease, border-color 0.3s ease',
        overflow: 'hidden',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexShrink: 0 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: theme.text }}>{title}</span>
        {action && (
          <span style={{ fontSize: 11, color: actionColor || theme.accentText, fontWeight: 500, cursor: 'pointer' }}>
            {action}
          </span>
        )}
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>{children}</div>
    </div>
  )
}
