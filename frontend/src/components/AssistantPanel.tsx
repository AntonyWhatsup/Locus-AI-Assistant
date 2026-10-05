import { useEffect, useState, type ReactNode } from 'react'
import type { Theme } from '../themes'
import type { AppStatus, ConnectionStatus } from '../App'

const catMessages: Record<AppStatus, string> = {
  initializing: 'Starting',
  idle: 'Go ahead',
  listening: 'Listening...',
  processing: '...',
  speaking: 'Say that again!',
  error: 'Check status',
}

const nyanMessages: Record<AppStatus, string> = {
  initializing: 'bootin',
  idle: 'can i haz?',
  listening: 'im listenin',
  processing: 'big thonk...',
  speaking: 'meow meow',
  error: 'halp',
}

export default function AssistantPanel({
  theme,
  status,
  catImage,
  statusTitle,
  statusText,
  connectionStatus,
  onListen,
  onOpenSettings,
}: {
  theme: Theme
  status: AppStatus
  catImage: string
  statusTitle: string
  statusText: string
  connectionStatus: ConnectionStatus
  onListen: () => void
  onOpenSettings: () => void
}) {
  const isNyan = theme.name === 'cat'
  const overlayText = isNyan ? nyanMessages[status] : catMessages[status]
  const [imageMissing, setImageMissing] = useState(false)
  const canListen = status === 'idle' || status === 'error'
  const canStop = status === 'listening'
  const disabled = connectionStatus !== 'connected' || (!canListen && !canStop)
  const buttonLabel = canStop ? 'Stop' : status === 'processing' || status === 'initializing' ? 'Processing' : 'Listen'
  const imageSrc = `/cat_${catImage}.jpg`

  useEffect(() => {
    setImageMissing(false)
  }, [imageSrc])

  return (
    <Panel theme={theme} title={isNyan ? 'Cat Assistant' : 'Assistant'} action={connectionStatus === 'connected' ? 'Local session' : 'Offline'}>
      <div style={{ display: 'flex', gap: 16, height: '100%' }}>
        <button
          onClick={onListen}
          disabled={disabled}
          aria-label={canStop ? 'Stop listening' : 'Start listening'}
          style={{
            width: 'clamp(132px, 32%, 190px)',
            aspectRatio: '1 / 1',
            flexShrink: 0,
            borderRadius: 10,
            overflow: 'hidden',
            cursor: disabled ? 'not-allowed' : 'pointer',
            position: 'relative',
            background: `linear-gradient(145deg, ${theme.inputBg}, ${theme.panelBg})`,
            border: 'none',
            padding: 0,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div
            style={{
              flex: 1,
              minHeight: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 8,
            }}
          >
            {imageMissing ? (
              <span style={{ color: theme.subtext, fontSize: 12, fontWeight: 700 }}>Image unavailable</span>
            ) : (
              <img
                src={imageSrc}
                alt="Assistant cat"
                onError={() => setImageMissing(true)}
                style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block', opacity: 0.95 }}
              />
            )}
          </div>
          <div
            style={{
              flexShrink: 0,
              minHeight: 30,
              padding: '6px 8px',
              background: 'rgba(0,0,0,0.36)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderTop: `1px solid ${theme.panelBorder}`,
            }}
          >
            <span
              style={{
                color: theme.accent,
                fontWeight: 800,
                fontSize: 14,
                textShadow: `0 0 12px ${theme.accent}`,
                letterSpacing: 0,
              }}
            >
              {overlayText}
            </span>
          </div>
        </button>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div>
            <p style={{ fontSize: 13, fontWeight: 600, color: theme.text, marginBottom: 2 }}>Control Deck</p>
            <p style={{ fontSize: 11, color: theme.subtext, lineHeight: 1.4 }}>
              {statusTitle}: {statusText}
            </p>
          </div>

          <button
            onClick={onListen}
            disabled={disabled}
            style={{
              background: canListen ? theme.listenBtn : `${theme.accent}44`,
              color: canListen ? theme.listenBtnText : theme.accentText,
              border: `1px solid ${theme.accent}`,
              borderRadius: 8,
              padding: '10px 0',
              fontWeight: 700,
              fontSize: 13,
              cursor: disabled ? 'not-allowed' : 'pointer',
              opacity: disabled ? 0.6 : 1,
              letterSpacing: 0,
              transition: 'all 0.25s ease',
              boxShadow: canListen ? `0 0 16px ${theme.accent}44` : 'none',
            }}
          >
            {buttonLabel}
          </button>

          <button
            onClick={onOpenSettings}
            style={{
              background: theme.inputBg,
              color: theme.text,
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
              {connectionStatus === 'connected' ? 'Local Link Ready' : 'Reconnecting'}
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
  children: ReactNode
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
          <span style={{ fontSize: 11, color: actionColor || theme.accentText, fontWeight: 500 }}>
            {action}
          </span>
        )}
      </div>
      <div style={{ flex: 1, minHeight: 0 }}>{children}</div>
    </div>
  )
}
