import type { Theme } from '../themes'

const navItems = [
  { id: 'HOME', icon: HomeIcon },
  { id: 'MIC', icon: MicIcon },
  { id: 'CHAT', icon: ChatIcon },
  { id: 'SET', icon: SettingsIcon },
  { id: 'VOICE', icon: VoiceIcon, bottom: true },
]

export default function Sidebar({ theme, status }: { theme: Theme; status: string }) {
  const isActive = (id: string) => id === 'HOME'

  return (
    <div
      style={{
        width: 64,
        background: theme.sidebar,
        backdropFilter: 'blur(20px) saturate(1.3)',
        WebkitBackdropFilter: 'blur(20px) saturate(1.3)',
        borderRight: `1px solid ${theme.panelBorder}`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        paddingTop: 20,
        paddingBottom: 20,
        gap: 0,
        position: 'relative',
        flexShrink: 0,
        transition: 'background 0.3s ease',
      }}
    >
      {/* Accent bar */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 16,
          bottom: 16,
          width: 4,
          borderRadius: '0 4px 4px 0',
          background: theme.sidebarAccent,
          boxShadow: `0 0 12px ${theme.sidebarAccent}88`,
        }}
      />

      {/* Status dot */}
      <div
        className="pulse-dot"
        style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: status === 'idle' ? theme.subtext : theme.accent,
          marginBottom: 24,
          boxShadow: status !== 'idle' ? `0 0 8px ${theme.accent}` : 'none',
          transition: 'background 0.3s ease, box-shadow 0.3s ease',
        }}
      />

      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, flex: 1 }}>
        {navItems.filter(i => !i.bottom).map(item => (
          <NavItem key={item.id} item={item} theme={theme} active={isActive(item.id)} />
        ))}
      </div>

      <div style={{ marginTop: 'auto' }}>
        {navItems.filter(i => i.bottom).map(item => (
          <NavItem key={item.id} item={item} theme={theme} active={false} />
        ))}
      </div>
    </div>
  )
}

function NavItem({ item, theme, active }: { item: typeof navItems[0]; theme: Theme; active: boolean }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 4,
        padding: '10px 0',
        cursor: 'pointer',
        borderRadius: 8,
        background: active ? theme.accentDim : 'transparent',
        width: 48,
        transition: 'background 0.2s ease',
      }}
    >
      <item.icon
        size={18}
        color={active ? theme.accent : theme.subtext}
      />
      <span style={{ fontSize: 9, color: active ? theme.accentText : theme.subtext, letterSpacing: '0.05em', fontWeight: 600 }}>
        {item.id}
      </span>
    </div>
  )
}

function HomeIcon({ size, color }: { size: number; color: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" stroke={color} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" />
      <polyline points="9,22 9,12 15,12 15,22" stroke={color} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
function MicIcon({ size, color }: { size: number; color: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <rect x="9" y="2" width="6" height="11" rx="3" stroke={color} strokeWidth={1.8} />
      <path d="M5 10a7 7 0 0014 0" stroke={color} strokeWidth={1.8} strokeLinecap="round" />
      <line x1="12" y1="19" x2="12" y2="22" stroke={color} strokeWidth={1.8} strokeLinecap="round" />
    </svg>
  )
}
function ChatIcon({ size, color }: { size: number; color: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z" stroke={color} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
function SettingsIcon({ size, color }: { size: number; color: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="3" stroke={color} strokeWidth={1.8} />
      <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z" stroke={color} strokeWidth={1.8} />
    </svg>
  )
}
function VoiceIcon({ size, color }: { size: number; color: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" stroke={color} strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round" />
      <path d="M19.07 4.93a10 10 0 010 14.14" stroke={color} strokeWidth={1.8} strokeLinecap="round" />
      <path d="M15.54 8.46a5 5 0 010 7.07" stroke={color} strokeWidth={1.8} strokeLinecap="round" />
    </svg>
  )
}
