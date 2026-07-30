import type { ThemeName } from './themes'

export type AppStatus = 'initializing' | 'idle' | 'listening' | 'processing' | 'speaking' | 'error'
export type ConnectionStatus = 'connecting' | 'connected' | 'reconnecting' | 'disconnected'
export type MessageAuthor = 'user' | 'locus' | 'system'

export interface ChatMessage {
  from: MessageAuthor
  text: string
}

export interface RuntimeSnapshot {
  type: 'snapshot'
  state: 'initializing' | 'ready' | 'listening' | 'processing' | 'speaking' | 'error'
  status: StatusEvent
  mic_state: MicStateEvent
  image: string
  mic_level: number
  visualizer: VisualizerEvent
  transcript: {
    user_text?: string | null
    locus_text?: string | null
  }
  settings?: {
    theme?: string
  }
}

export interface StatusEvent {
  type: 'status'
  title: string
  tone: 'idle' | 'listening' | 'thinking' | 'speaking' | 'success' | 'prompt' | 'error'
  text: string
}

export interface MicStateEvent {
  type: 'mic_state'
  state: 'idle' | 'listening' | 'thinking' | 'speaking' | 'success' | 'prompt' | 'error'
  msg: string
}

export interface TranscriptEvent {
  type: 'transcript'
  user_text?: string | null
  locus_text?: string | null
}

export interface ImageEvent {
  type: 'image'
  image: string
}

export interface MicLevelEvent {
  type: 'mic_level'
  level: number
}

export interface VisualizerEvent {
  type: 'visualizer'
  state: 'start' | 'stop'
  text?: string | null
}

export interface CommandAckEvent {
  type: 'command_ack'
  action: 'listen' | 'stop'
  accepted: boolean
  state: RuntimeSnapshot['state']
  message: string
}

export interface ErrorEvent {
  type: 'error'
  code: string
  message: string
}

export interface ConversationClearedEvent {
  type: 'conversation_cleared'
}

export type ServerEvent =
  | RuntimeSnapshot
  | StatusEvent
  | MicStateEvent
  | TranscriptEvent
  | ImageEvent
  | MicLevelEvent
  | VisualizerEvent
  | CommandAckEvent
  | ErrorEvent
  | ConversationClearedEvent

export interface SessionResponse {
  ws_token: string
  ws_path: string
}

const statusMap: Record<StatusEvent['tone'], AppStatus> = {
  idle: 'idle',
  listening: 'listening',
  thinking: 'processing',
  speaking: 'speaking',
  success: 'idle',
  prompt: 'listening',
  error: 'error',
}

export function normalizeThemeName(value: unknown): ThemeName {
  const normalized = String(value ?? '').trim().replace('_', '-').toLowerCase()
  if (normalized === 'glass-green' || normalized === 'glassgreen') return 'glass-green'
  if (normalized === 'nyan' || normalized === 'cat') return 'cat'
  if (normalized === 'dark' || normalized === 'light' || normalized === 'colorful') return normalized
  return 'glass-green'
}

export function stateToStatus(state: RuntimeSnapshot['state']): AppStatus {
  if (state === 'ready') return 'idle'
  return state
}

export function toneToStatus(tone: StatusEvent['tone']): AppStatus {
  return statusMap[tone]
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isString(value: unknown): value is string {
  return typeof value === 'string'
}

function isNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isFinite(value)
}

export function parseServerEvent(raw: string): ServerEvent | null {
  let parsed: unknown
  try {
    parsed = JSON.parse(raw)
  } catch {
    return null
  }

  if (!isObject(parsed) || !isString(parsed.type)) return null

  switch (parsed.type) {
    case 'snapshot':
      if (!isString(parsed.state) || !isString(parsed.image) || !isNumber(parsed.mic_level)) return null
      if (!isObject(parsed.status) || !isObject(parsed.mic_state) || !isObject(parsed.visualizer)) return null
      return parsed as unknown as RuntimeSnapshot
    case 'status':
      if (!isString(parsed.title) || !isString(parsed.tone) || !isString(parsed.text)) return null
      return parsed as unknown as StatusEvent
    case 'mic_state':
      if (!isString(parsed.state) || !isString(parsed.msg)) return null
      return parsed as unknown as MicStateEvent
    case 'transcript':
      return parsed as unknown as TranscriptEvent
    case 'image':
      if (!isString(parsed.image)) return null
      return parsed as unknown as ImageEvent
    case 'mic_level':
      if (!isNumber(parsed.level)) return null
      return parsed as unknown as MicLevelEvent
    case 'visualizer':
      if (parsed.state !== 'start' && parsed.state !== 'stop') return null
      return parsed as unknown as VisualizerEvent
    case 'command_ack':
      if (!isString(parsed.action) || typeof parsed.accepted !== 'boolean' || !isString(parsed.message)) return null
      return parsed as unknown as CommandAckEvent
    case 'error':
      if (!isString(parsed.code) || !isString(parsed.message)) return null
      return parsed as unknown as ErrorEvent
    case 'conversation_cleared':
      return parsed as unknown as ConversationClearedEvent
    default:
      return null
  }
}

export function buildApiBaseUrl(): string {
  const configured = import.meta.env.VITE_LOCUS_API_BASE_URL
  if (configured) return String(configured).replace(/\/$/, '')
  return window.location.origin
}

export function buildWebSocketUrl(path: string, token: string): string {
  const configured = import.meta.env.VITE_LOCUS_WS_URL
  const base = configured ? new URL(configured) : new URL(path, buildApiBaseUrl())
  if (base.protocol === 'http:') base.protocol = 'ws:'
  if (base.protocol === 'https:') base.protocol = 'wss:'
  base.searchParams.set('token', token)
  return base.toString()
}
