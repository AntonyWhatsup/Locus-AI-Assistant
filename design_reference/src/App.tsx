import { useState } from 'react'
import { themes, type ThemeName, type Theme } from './themes'
import Sidebar from './components/Sidebar'
import TopBar from './components/TopBar'
import AssistantPanel from './components/AssistantPanel'
import VoicePanel from './components/VoicePanel'
import ConversationPanel from './components/ConversationPanel'
import SessionPanel from './components/SessionPanel'

export type AppStatus = 'idle' | 'listening' | 'thinking' | 'speaking'

export default function App() {
  const [themeName, setThemeName] = useState<ThemeName>('glass-green')
  const [status, setStatus] = useState<AppStatus>('idle')
  const [messages, setMessages] = useState([
    { from: 'user', text: 'Waiting for your command.' },
    { from: 'locus', text: 'Say that again for me.' },
  ])

  const theme = themes[themeName]

  const handleListen = () => {
    if (status === 'idle') {
      setStatus('listening')
      setTimeout(() => setStatus('thinking'), 3000)
      setTimeout(() => {
        setStatus('speaking')
        setMessages(prev => [
          ...prev,
          { from: 'user', text: 'Hey Locus, what time is it?' },
          { from: 'locus', text: "It's 7:42 PM. Anything else?" },
        ])
      }, 4500)
      setTimeout(() => setStatus('idle'), 7000)
    } else {
      setStatus('idle')
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        fontFamily: "'Inter', 'SF Pro Display', system-ui, sans-serif",
        color: theme.text,
        transition: 'color 0.3s ease',
        position: 'relative',
        overflow: 'hidden',
        background: themeName === 'glass-green' || themeName === 'cat'
          ? 'transparent'
          : theme.bg,
      }}
    >
      {/* Nyan cat vaporwave background */}
      {themeName === 'cat' && (
        <div style={{ position: 'absolute', inset: 0, zIndex: 0, overflow: 'hidden' }}>
          {/* Deep purple base */}
          <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 0%, #2a0040 0%, #0d0018 60%, #08000f 100%)' }} />
          {/* Retro perspective grid */}
          <div style={{
            position: 'absolute',
            bottom: 0,
            left: '-20%',
            right: '-20%',
            height: '55%',
            backgroundImage: 'linear-gradient(rgba(255,45,160,0.35) 1px, transparent 1px), linear-gradient(90deg, rgba(255,45,160,0.35) 1px, transparent 1px)',
            backgroundSize: '60px 60px',
            transform: 'perspective(280px) rotateX(62deg)',
            transformOrigin: 'bottom center',
          }} />
          {/* Horizon glow line */}
          <div style={{ position: 'absolute', left: 0, right: 0, bottom: '54%', height: 2, background: 'linear-gradient(90deg, transparent, #ff2d78, #ff80c0, #ff2d78, transparent)', opacity: 0.8 }} />
          {/* Pink top ambient blob */}
          <div style={{ position: 'absolute', top: '-15%', left: '30%', width: 700, height: 500, borderRadius: '50%', background: 'radial-gradient(circle, rgba(255,45,160,0.22) 0%, transparent 70%)', filter: 'blur(50px)' }} />
          {/* Cyan bottom-left blob */}
          <div style={{ position: 'absolute', bottom: '20%', left: '-5%', width: 350, height: 350, borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,220,255,0.18) 0%, transparent 70%)', filter: 'blur(40px)' }} />
          {/* Stars */}
          {[...Array(30)].map((_, i) => (
            <div key={i} style={{
              position: 'absolute',
              width: i % 4 === 0 ? 2 : 1,
              height: i % 4 === 0 ? 2 : 1,
              borderRadius: '50%',
              background: i % 3 === 0 ? '#ff80c0' : '#ffffff',
              top: `${(i * 37 + 11) % 60}%`,
              left: `${(i * 53 + 7) % 100}%`,
              opacity: 0.4 + (i % 5) * 0.1,
            }} />
          ))}
        </div>
      )}

      {/* Glass Green background scene */}
      {themeName === 'glass-green' && (
        <div style={{ position: 'absolute', inset: 0, zIndex: 0 }}>
          <img
            src="https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?w=1600&h=1000&fit=crop&auto=format"
            alt=""
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
          />
          <div style={{ position: 'absolute', inset: 0, background: 'rgba(2,18,8,0.62)' }} />
          {/* Green ambient glow blobs */}
          <div style={{ position: 'absolute', top: '-10%', left: '20%', width: 600, height: 600, borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,255,100,0.18) 0%, transparent 70%)', filter: 'blur(40px)' }} />
          <div style={{ position: 'absolute', bottom: '-5%', right: '10%', width: 400, height: 400, borderRadius: '50%', background: 'radial-gradient(circle, rgba(0,200,80,0.12) 0%, transparent 70%)', filter: 'blur(40px)' }} />
        </div>
      )}
      <div style={{ position: 'relative', zIndex: 1, display: 'flex', width: '100%' }}>
      <Sidebar theme={theme} status={status} />

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <TopBar
          theme={theme}
          themeName={themeName}
          setThemeName={setThemeName}
          status={status}
        />

        <main
          style={{
            flex: 1,
            padding: '20px 24px 24px',
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gridTemplateRows: '1fr 1fr',
            gap: '16px',
            overflow: 'auto',
          }}
        >
          <AssistantPanel theme={theme} status={status} onListen={handleListen} />
          <VoicePanel theme={theme} status={status} />
          <ConversationPanel theme={theme} messages={messages} />
          <SessionPanel theme={theme} />
        </main>
      </div>
      </div>
    </div>
  )
}
