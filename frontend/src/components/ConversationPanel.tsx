import { useEffect, useRef } from 'react'
import { Panel } from './AssistantPanel'
import type { ChatMessage } from '../App'
import type { Theme } from '../themes'

export default function ConversationPanel({ theme, messages }: { theme: Theme; messages: ChatMessage[] }) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <Panel theme={theme} title="Conversation" action="Live Preview" actionColor={theme.accentText}>
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
          overflowY: 'auto',
          maxHeight: 180,
          paddingRight: 4,
        }}
      >
        {messages.map((msg, i) => (
          <MessageBubble key={i} msg={msg} theme={theme} />
        ))}
        <div ref={bottomRef} />
      </div>
    </Panel>
  )
}

function MessageBubble({ msg, theme }: { msg: ChatMessage; theme: Theme }) {
  const isUser = msg.from === 'user'
  const label = msg.from === 'system' ? 'System' : isUser ? 'You' : 'Locus'
  return (
    <div
      style={{
        background: isUser ? theme.inputBg : theme.accentDim,
        border: `1px solid ${isUser ? theme.panelBorder : theme.accent + '33'}`,
        borderRadius: 10,
        padding: '10px 14px',
      }}
    >
      <div
        style={{
          fontSize: 10,
          fontWeight: 700,
          color: isUser ? theme.subtext : theme.accentText,
          marginBottom: 4,
          textTransform: 'uppercase',
          letterSpacing: 0,
        }}
      >
        {label}
      </div>
      <p style={{ fontSize: 13, color: theme.text, lineHeight: 1.5 }}>{msg.text}</p>
    </div>
  )
}
