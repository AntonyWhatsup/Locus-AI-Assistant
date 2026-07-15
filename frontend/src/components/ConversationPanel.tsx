import { useEffect, useRef } from 'react'
import { Panel } from './AssistantPanel'
import type { Theme } from '../themes'

interface Message {
  from: 'user' | 'locus'
  text: string
}

export default function ConversationPanel({ theme, messages }: { theme: Theme; messages: Message[] }) {
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

function MessageBubble({ msg, theme }: { msg: { from: string; text: string }; theme: Theme }) {
  const isUser = msg.from === 'user'
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
          letterSpacing: '0.08em',
        }}
      >
        {isUser ? 'You' : 'Locus'}
      </div>
      <p style={{ fontSize: 13, color: theme.text, lineHeight: 1.5 }}>{msg.text}</p>
    </div>
  )
}
