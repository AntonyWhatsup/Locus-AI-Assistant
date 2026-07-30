import type { CSSProperties } from 'react'
import { Panel } from './AssistantPanel'
import type { Theme } from '../themes'
import type { AppStatus } from '../App'

const statusInfo: Record<AppStatus, { label: string; sub: string; voiceLabel: string; voiceSub: string }> = {
  initializing: {
    label: 'Initializing',
    sub: 'Backend is preparing the local model.',
    voiceLabel: 'Voice Activity',
    voiceSub: 'Not ready yet',
  },
  idle: {
    label: "Say 'Locus'",
    sub: 'Left-click the cat or wait for the wake word.',
    voiceLabel: 'Voice Activity',
    voiceSub: 'Waiting for activation',
  },
  listening: {
    label: 'Listening...',
    sub: 'Speak clearly near the microphone.',
    voiceLabel: 'Voice Activity',
    voiceSub: 'Live microphone input',
  },
  processing: {
    label: 'Processing...',
    sub: 'Analyzing your command.',
    voiceLabel: 'Voice Activity',
    voiceSub: 'Processing command',
  },
  speaking: {
    label: 'Speaking',
    sub: 'Locus is responding.',
    voiceLabel: 'Voice Activity',
    voiceSub: 'Audio output active',
  },
  error: {
    label: 'Needs Attention',
    sub: 'Check the latest status before listening again.',
    voiceLabel: 'Voice Activity',
    voiceSub: 'Unavailable',
  },
}

const BAR_COUNT = 28
const bars = Array.from({ length: BAR_COUNT }, (_, i) => i)

export default function VoicePanel({
  theme,
  status,
  micLevel,
  micStateText,
  visualizerActive,
  visualizerText,
}: {
  theme: Theme
  status: AppStatus
  micLevel: number
  micStateText: string
  visualizerActive: boolean
  visualizerText: string
}) {
  const info = statusInfo[status]
  const isActive = visualizerActive || status === 'listening'
  const activeLevel = Math.max(0, Math.min(1, micLevel))

  return (
    <Panel
      theme={theme}
      title={info.label}
      action={status === 'idle' ? 'Idle' : status === 'listening' ? 'Listening' : status === 'processing' ? 'Processing' : status === 'error' ? 'Error' : 'Starting'}
      actionColor={theme.accentText}
    >
      <p style={{ fontSize: 11, color: theme.subtext, marginBottom: 12, marginTop: -4 }}>
        {visualizerText || micStateText || info.sub}
      </p>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
        <span style={{ fontSize: 12, fontWeight: 600, color: theme.text }}>{info.voiceLabel}</span>
        <span style={{ fontSize: 11, color: isActive ? theme.accentText : theme.subtext, fontWeight: 500 }}>
          {isActive ? `${Math.round(activeLevel * 100)}%` : info.voiceSub}
        </span>
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: 3,
          height: 56,
          padding: '0 4px',
        }}
      >
        {bars.map(i => {
          const wave = 0.4 + Math.abs(Math.sin(i * 0.55)) * 0.6
          const maxH = 4 + (activeLevel * 48 * wave)
          return (
            <div
              key={i}
              className="waveform-bar"
              style={{
                flex: 1,
                background: isActive
                  ? i % 3 === 0
                    ? theme.accent
                    : `${theme.accent}88`
                  : `${theme.subtext}44`,
                '--bar-max': `${maxH}px`,
                '--bar-dur': `${0.4 + (i % 5) * 0.12}s`,
                '--bar-delay': `${(i % 7) * 0.06}s`,
                animationPlayState: isActive ? 'running' : 'paused',
                height: isActive ? undefined : `${4 + activeLevel * 16 * wave}px`,
                transition: 'background 0.3s ease',
              } as CSSProperties}
            />
          )
        })}
      </div>

      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          gap: 2,
          height: 32,
          marginTop: 10,
          borderTop: `1px solid ${theme.panelBorder}`,
          paddingTop: 8,
        }}
      >
        {Array.from({ length: 20 }, (_, i) => (
          <div
            key={i}
            style={{
              flex: 1,
              height: `${4 + activeLevel * (8 + Math.abs(Math.sin(i * 0.7 + 1)) * 18)}px`,
              background: `${theme.subtext}33`,
              borderRadius: 2,
            }}
          />
        ))}
      </div>
    </Panel>
  )
}
