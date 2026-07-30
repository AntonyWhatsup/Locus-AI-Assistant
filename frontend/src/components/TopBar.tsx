import type { AppStatus, ConnectionStatus } from '../App'
import type { Theme, ThemeName } from '../themes'

const themeOrder: ThemeName[] = ['glass-green', 'dark', 'light', 'colorful', 'cat']
const themeLabels: Record<ThemeName, string> = {
  'glass-green': 'Glass Green',
  dark: 'Dark',
  light: 'Light',
  colorful: 'Colorful',
  cat: 'Nyan',
}

const statusLabels: Record<AppStatus, string> = {
  initializing: 'Starting',
  idle: 'Idle',
  listening: 'Listening',
  processing: 'Processing',
  speaking: 'Speaking',
  error: 'Error',
}

const connectionLabels: Record<ConnectionStatus, string> = {
  connecting: 'Connecting',
  connected: 'Connected',
  reconnecting: 'Reconnecting',
  disconnected: 'Disconnected',
}

export default function TopBar({
  theme,
  themeName,
  setThemeName,
  status,
  connectionStatus,
}: {
  theme: Theme
  themeName: ThemeName
  setThemeName: (t: ThemeName) => void
  status: AppStatus
  connectionStatus: ConnectionStatus
}) {
  return (
    <header
      className="top-bar"
      style={{
        padding: '16px 24px',
        display: 'flex',
        alignItems: 'center',
        gap: 16,
        borderBottom: `1px solid ${theme.panelBorder}`,
        background: theme.sidebar,
        backdropFilter: 'blur(20px) saturate(1.3)',
        WebkitBackdropFilter: 'blur(20px) saturate(1.3)',
        flexShrink: 0,
        transition: 'background 0.3s ease',
      }}
    >
      <div style={{ flex: 1, minWidth: 180 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: theme.text, letterSpacing: 0, lineHeight: 1.1 }}>
          Locus AI
        </h1>
        <p style={{ fontSize: 12, color: theme.subtext, marginTop: 2 }}>
          Local voice assistant runtime
        </p>
      </div>

      <div
        aria-disabled="true"
        title="Search is not available in this build."
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          background: theme.inputBg,
          border: `1px solid ${theme.panelBorder}`,
          borderRadius: 8,
          padding: '7px 12px',
          width: 180,
          opacity: 0.65,
        }}
      >
        <svg width={14} height={14} viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <circle cx="11" cy="11" r="8" stroke={theme.subtext} strokeWidth={2} />
          <line x1="21" y1="21" x2="16.65" y2="16.65" stroke={theme.subtext} strokeWidth={2} strokeLinecap="round" />
        </svg>
        <input
          disabled
          placeholder="Search unavailable"
          aria-label="Search unavailable"
          style={{
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: theme.text,
            fontSize: 13,
            width: '100%',
          }}
        />
      </div>

      <div
        role="radiogroup"
        aria-label="Theme"
        style={{
          display: 'flex',
          gap: 4,
          background: theme.inputBg,
          border: `1px solid ${theme.panelBorder}`,
          borderRadius: 8,
          padding: 4,
        }}
      >
        {themeOrder.map(t => (
          <button
            key={t}
            onClick={() => setThemeName(t)}
            aria-label={`Use ${themeLabels[t]} theme`}
            aria-pressed={themeName === t}
            style={{
              padding: '4px 10px',
              borderRadius: 5,
              border: 'none',
              cursor: 'pointer',
              fontSize: 11,
              fontWeight: 600,
              background: themeName === t ? theme.accent : 'transparent',
              color: themeName === t ? theme.listenBtnText : theme.subtext,
              transition: 'all 0.2s ease',
              letterSpacing: 0,
            }}
          >
            {themeLabels[t]}
          </button>
        ))}
      </div>

      <div
        title={`WebSocket ${connectionLabels[connectionStatus]}`}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          background: theme.statusBadge,
          border: `1px solid ${theme.accentText}33`,
          borderRadius: 20,
          padding: '5px 12px',
        }}
      >
        <div
          className="pulse-dot"
          style={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            background: theme.accentText,
            boxShadow: `0 0 6px ${theme.accentText}`,
          }}
        />
        <span style={{ fontSize: 12, color: theme.accentText, fontWeight: 600 }}>
          {statusLabels[status]} / {connectionLabels[connectionStatus]}
        </span>
      </div>
    </header>
  )
}
