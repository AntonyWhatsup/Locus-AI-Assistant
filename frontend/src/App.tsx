import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { themes, type ThemeName } from './themes'
import Sidebar from './components/Sidebar'
import TopBar from './components/TopBar'
import AssistantPanel from './components/AssistantPanel'
import VoicePanel from './components/VoicePanel'
import ConversationPanel from './components/ConversationPanel'
import SessionPanel from './components/SessionPanel'
import SettingsPanel from './components/SettingsPanel'
import type { SettingsData } from './settingsTypes'
import {
  buildApiBaseUrl,
  buildWebSocketUrl,
  normalizeThemeName,
  parseServerEvent,
  stateToStatus,
  toneToStatus,
  type AppStatus,
  type ChatMessage,
  type ConnectionStatus,
  type ServerEvent,
  type SessionResponse,
} from './ws'

export type { AppStatus, ChatMessage, ConnectionStatus }

const THEME_STORAGE_KEY = 'locus.theme'

interface RuntimeUiState {
  status: AppStatus
  statusTitle: string
  statusText: string
  micStateText: string
  catImage: string
  micLevel: number
  visualizerActive: boolean
  visualizerText: string
  messages: ChatMessage[]
  showLiveTranscript: boolean
}

const initialUiState: RuntimeUiState = {
  status: 'initializing',
  statusTitle: 'Connecting',
  statusText: 'Opening a local session.',
  micStateText: 'Waiting for backend connection.',
  catImage: 'train',
  micLevel: 0,
  visualizerActive: false,
  visualizerText: '',
  messages: [{ from: 'system', text: 'Connecting to Locus API.' }],
  showLiveTranscript: true,
}

function appendMessages(current: ChatMessage[], event: { user_text?: string | null; locus_text?: string | null }, showLiveTranscript: boolean) {
  const next = [...current]
  if (showLiveTranscript && event.user_text) next.push({ from: 'user', text: event.user_text })
  if (event.locus_text) next.push({ from: 'locus', text: event.locus_text })
  return next.slice(-40)
}

function applyEvent(state: RuntimeUiState, event: ServerEvent): RuntimeUiState {
  switch (event.type) {
    case 'snapshot':
      return {
        ...state,
        status: stateToStatus(event.state),
        statusTitle: event.status.title,
        statusText: event.status.text,
        micStateText: event.mic_state.msg,
        catImage: event.image,
        micLevel: event.mic_level,
        visualizerActive: event.visualizer.state === 'start',
        visualizerText: event.visualizer.text ?? '',
        messages: appendMessages([], event.transcript, state.showLiveTranscript),
      }
    case 'status':
      return {
        ...state,
        status: toneToStatus(event.tone),
        statusTitle: event.title,
        statusText: event.text,
      }
    case 'mic_state':
      return {
        ...state,
        status: toneToStatus(event.state),
        micStateText: event.msg,
      }
    case 'image':
      return {
        ...state,
        catImage: event.image,
      }
    case 'mic_level':
      return {
        ...state,
        micLevel: Math.max(0, Math.min(1, event.level)),
      }
    case 'visualizer':
      return {
        ...state,
        visualizerActive: event.state === 'start',
        visualizerText: event.text ?? '',
        micLevel: event.state === 'stop' ? 0 : state.micLevel,
      }
    case 'transcript':
      return {
        ...state,
        messages: appendMessages(state.messages, event, state.showLiveTranscript),
      }
    case 'command_ack':
      return event.accepted
        ? state
        : {
            ...state,
            messages: [...state.messages, { from: 'system' as const, text: event.message }].slice(-40),
          }
    case 'error':
      return {
        ...state,
        messages: [...state.messages, { from: 'system' as const, text: event.message }].slice(-40),
      }
    case 'conversation_cleared':
      return {
        ...state,
        messages: [],
      }
  }
}

function readStoredTheme(): ThemeName {
  return normalizeThemeName(window.localStorage.getItem(THEME_STORAGE_KEY))
}

export default function App() {
  const [themeName, setThemeNameState] = useState<ThemeName>(readStoredTheme)
  const [uiState, setUiState] = useState<RuntimeUiState>(initialUiState)
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('connecting')
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [sessionTokenValue, setSessionTokenValue] = useState<string | null>(null)
  const ws = useRef<WebSocket | null>(null)
  const reconnectTimer = useRef<number | null>(null)
  const reconnectAttempt = useRef(0)
  const sessionToken = useRef<string | null>(null)
  const shouldReconnect = useRef(true)
  const settingsOpener = useRef<HTMLElement | null>(null)

  const theme = themes[themeName]
  const apiBaseUrl = useMemo(buildApiBaseUrl, [])

  const saveTheme = useCallback(
    (nextTheme: ThemeName) => {
      window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme)
      if (!sessionToken.current) return
      void fetch(`${apiBaseUrl}/api/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Locus-Session': sessionToken.current,
        },
        body: JSON.stringify({ theme: nextTheme }),
      }).catch(() => undefined)
    },
    [apiBaseUrl],
  )

  const setThemeName = useCallback(
    (nextTheme: ThemeName) => {
      setThemeNameState(nextTheme)
      saveTheme(nextTheme)
    },
    [saveTheme],
  )

  const previewThemeName = useCallback((nextTheme: ThemeName) => {
    setThemeNameState(nextTheme)
  }, [])

  const persistSavedThemeName = useCallback((nextTheme: ThemeName) => {
    window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme)
    setThemeNameState(nextTheme)
  }, [])

  const applySavedSettings = useCallback((settings: SettingsData) => {
    setUiState(current => ({ ...current, showLiveTranscript: settings.show_live_transcript }))
  }, [])

  const sendCommand = useCallback((action: 'listen' | 'stop') => {
    const socket = ws.current
    if (!socket || socket.readyState !== WebSocket.OPEN) return
    socket.send(JSON.stringify({ action }))
  }, [])

  const handleListenToggle = useCallback(() => {
    if (uiState.status === 'listening') {
      sendCommand('stop')
      return
    }
    if (uiState.status === 'idle' || uiState.status === 'error') {
      sendCommand('listen')
    }
  }, [sendCommand, uiState.status])

  const openSettings = useCallback(() => {
    settingsOpener.current = document.activeElement instanceof HTMLElement ? document.activeElement : null
    setSettingsOpen(true)
  }, [])

  const closeSettings = useCallback(() => {
    setSettingsOpen(false)
    window.setTimeout(() => settingsOpener.current?.focus(), 0)
  }, [])

  const clearConversation = useCallback(async () => {
    if (!sessionToken.current) throw new Error('Backend session is not ready.')
    const response = await fetch(`${apiBaseUrl}/api/conversation/clear`, {
      method: 'POST',
      headers: { 'X-Locus-Session': sessionToken.current },
    })
    if (!response.ok) throw new Error(`Clear failed with ${response.status}.`)
    setUiState(current => ({ ...current, messages: [] }))
  }, [apiBaseUrl, applySavedSettings])

  useEffect(() => {
    shouldReconnect.current = true

    const clearReconnectTimer = () => {
      if (reconnectTimer.current !== null) {
        window.clearTimeout(reconnectTimer.current)
        reconnectTimer.current = null
      }
    }

    const scheduleReconnect = (connect: () => void) => {
      if (!shouldReconnect.current || reconnectTimer.current !== null) return
      reconnectAttempt.current += 1
      const delay = Math.min(12000, 800 * 2 ** Math.min(4, reconnectAttempt.current))
      setConnectionStatus('reconnecting')
      reconnectTimer.current = window.setTimeout(() => {
        reconnectTimer.current = null
        connect()
      }, delay)
    }

    const connect = async () => {
      clearReconnectTimer()
      if (!shouldReconnect.current || ws.current?.readyState === WebSocket.OPEN || ws.current?.readyState === WebSocket.CONNECTING) {
        return
      }

      setConnectionStatus(reconnectAttempt.current > 0 ? 'reconnecting' : 'connecting')

      try {
        if (!sessionToken.current) {
          const response = await fetch(`${apiBaseUrl}/api/session`)
          if (!response.ok) throw new Error(`Session request failed: ${response.status}`)
          const session = (await response.json()) as SessionResponse
          sessionToken.current = session.ws_token
          setSessionTokenValue(session.ws_token)
          void fetch(`${apiBaseUrl}/api/settings`)
            .then(response => (response.ok ? response.json() : null))
            .then((settings: SettingsData | null) => {
              if (settings) applySavedSettings(settings)
            })
            .catch(() => undefined)
          ws.current = new WebSocket(buildWebSocketUrl(session.ws_path, session.ws_token))
        } else {
          ws.current = new WebSocket(buildWebSocketUrl('/ws', sessionToken.current))
        }
      } catch {
        scheduleReconnect(connect)
        return
      }

      ws.current.onopen = () => {
        reconnectAttempt.current = 0
        setConnectionStatus('connected')
      }

      ws.current.onmessage = (event) => {
        if (typeof event.data !== 'string') return
        const parsed = parseServerEvent(event.data)
        if (!parsed) {
          console.warn('Ignored unknown Locus WebSocket event.')
          return
        }
        if (parsed.type === 'snapshot' && parsed.settings?.theme) {
          const backendTheme = normalizeThemeName(parsed.settings.theme)
          setThemeNameState(backendTheme)
          window.localStorage.setItem(THEME_STORAGE_KEY, backendTheme)
        }
        setUiState(current => applyEvent(current, parsed))
      }

      ws.current.onerror = () => {
        setConnectionStatus('reconnecting')
      }

      ws.current.onclose = () => {
        ws.current = null
        if (!shouldReconnect.current) {
          setConnectionStatus('disconnected')
          return
        }
        scheduleReconnect(connect)
      }
    }

    void connect()

    return () => {
      shouldReconnect.current = false
      clearReconnectTimer()
      ws.current?.close()
      ws.current = null
    }
  }, [apiBaseUrl])

  return (
    <div
      className="app-shell"
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
      {themeName === 'cat' && (
        <div style={{ position: 'absolute', inset: 0, zIndex: 0, overflow: 'hidden' }}>
          <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(ellipse at 50% 0%, #2a0040 0%, #0d0018 60%, #08000f 100%)' }} />
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
          <div style={{ position: 'absolute', left: 0, right: 0, bottom: '54%', height: 2, background: 'linear-gradient(90deg, transparent, #ff2d78, #ff80c0, #ff2d78, transparent)', opacity: 0.8 }} />
        </div>
      )}

      {themeName === 'glass-green' && (
        <div style={{ position: 'absolute', inset: 0, zIndex: 0, background: 'linear-gradient(135deg, #021208 0%, #07331b 42%, #0a1f12 100%)' }}>
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(216,245,229,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(216,245,229,0.05) 1px, transparent 1px)', backgroundSize: '44px 44px' }} />
          <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at 35% 20%, rgba(0,255,127,0.2), transparent 36%), radial-gradient(circle at 78% 78%, rgba(0,160,90,0.18), transparent 38%)' }} />
        </div>
      )}
      <div className="app-frame" style={{ position: 'relative', zIndex: 1, display: 'flex', width: '100%' }}>
        <Sidebar
          theme={theme}
          status={uiState.status}
          activeSection={settingsOpen ? 'settings' : 'home'}
          onOpenSettings={openSettings}
        />

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
          <TopBar
            theme={theme}
            themeName={themeName}
            setThemeName={setThemeName}
            status={uiState.status}
            connectionStatus={connectionStatus}
          />

          <main className="dashboard-grid">
            <AssistantPanel
              theme={theme}
              status={uiState.status}
              catImage={uiState.catImage}
              statusTitle={uiState.statusTitle}
              statusText={uiState.statusText}
              connectionStatus={connectionStatus}
              onListen={handleListenToggle}
              onOpenSettings={openSettings}
            />
            <VoicePanel
              theme={theme}
              status={uiState.status}
              micLevel={uiState.micLevel}
              micStateText={uiState.micStateText}
              visualizerActive={uiState.visualizerActive}
              visualizerText={uiState.visualizerText}
            />
            <ConversationPanel theme={theme} messages={uiState.messages} />
            <SessionPanel theme={theme} />
          </main>
        </div>
      </div>
      <SettingsPanel
        open={settingsOpen}
        theme={theme}
        apiBaseUrl={apiBaseUrl}
        sessionToken={sessionTokenValue}
        currentTheme={themeName}
        onPreviewTheme={previewThemeName}
        onSaveTheme={persistSavedThemeName}
        onSettingsSaved={applySavedSettings}
        onClose={closeSettings}
        onClearConversation={clearConversation}
      />
    </div>
  )
}
