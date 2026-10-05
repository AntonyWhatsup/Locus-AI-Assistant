import type { ThemeName } from './themes'

export type AiModel = 'local' | 'gemini'

export interface SettingsData {
  language_code: string
  wake_words: string[]
  gemini_model: string
  theme: ThemeName
  animation_speed: string
  microphone_sensitivity: number
  auto_listen_on_startup: boolean
  show_live_transcript: boolean
  ai_model: AiModel
  tts_voice: string
  debug_mode: boolean
  local_intent_cache: boolean
  microphone_device_id: string
  output_audio_device_id: string
  mcp_server_command: string
  mcp_default_tool: string
  mcp_enabled: boolean
}

export interface OptionMeta {
  label: string
  description?: string
  disabled?: boolean
  reason?: string
  requires_api_key?: boolean
  configured?: boolean
}

export interface SettingsOptions {
  languages: Record<string, OptionMeta>
  themes: Record<string, OptionMeta>
  ai_models: Record<string, OptionMeta>
  tts_voices: Array<{ id: string; label: string; language?: string }>
  tts_voice_unavailable_reason: string
}

export function normalizeWakeWord(value: string): string {
  return value.trim().toLowerCase()
}

export function normalizeSettings(raw: SettingsData): SettingsData {
  return {
    ...raw,
    wake_words: raw.wake_words.map(normalizeWakeWord).filter(Boolean),
    microphone_sensitivity: Math.max(0, Math.min(100, Number(raw.microphone_sensitivity) || 0)),
  }
}
