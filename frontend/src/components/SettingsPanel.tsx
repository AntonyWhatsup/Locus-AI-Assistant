import { useCallback, useEffect, useMemo, useRef, useState, type CSSProperties, type ReactNode } from 'react'
import { themes, type Theme, type ThemeName } from '../themes'
import { normalizeThemeName } from '../ws'
import {
  normalizeSettings,
  normalizeWakeWord,
  type AiModel,
  type SettingsData,
  type SettingsOptions,
} from '../settingsTypes'

type TabId = 'voice' | 'ai' | 'appearance' | 'advanced'

const tabs: Array<{ id: TabId; label: string }> = [
  { id: 'voice', label: 'Voice & Wake' },
  { id: 'ai', label: 'AI Model' },
  { id: 'appearance', label: 'Appearance' },
  { id: 'advanced', label: 'Advanced' },
]

const themeOrder: ThemeName[] = ['glass-green', 'dark', 'light', 'colorful', 'cat']

const fallbackSettings: SettingsData = {
  language_code: 'en-US',
  wake_words: ['locus'],
  gemini_model: 'gemini-2.5-flash',
  theme: 'glass-green',
  animation_speed: 'normal',
  microphone_sensitivity: 65,
  auto_listen_on_startup: false,
  show_live_transcript: true,
  ai_model: 'local',
  tts_voice: '',
  debug_mode: false,
  local_intent_cache: true,
  microphone_device_id: '',
  output_audio_device_id: '',
  mcp_server_command: '',
  mcp_default_tool: '',
  mcp_enabled: false,
}

function cloneSettings(settings: SettingsData): SettingsData {
  return { ...settings, wake_words: [...settings.wake_words] }
}

function parseErrorMessage(error: unknown): string {
  if (error instanceof Error) return error.message
  return 'Unexpected settings error.'
}

async function readError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: unknown }
    if (typeof payload.detail === 'string') return payload.detail
    if (payload.detail && typeof payload.detail === 'object') {
      return Object.entries(payload.detail as Record<string, unknown>)
        .map(([field, message]) => `${field}: ${String(message)}`)
        .join(' ')
    }
  } catch {
    return `Request failed with ${response.status}.`
  }
  return `Request failed with ${response.status}.`
}

export default function SettingsPanel({
  open,
  theme,
  apiBaseUrl,
  sessionToken,
  currentTheme,
  onPreviewTheme,
  onSaveTheme,
  onSettingsSaved,
  onClose,
  onClearConversation,
}: {
  open: boolean
  theme: Theme
  apiBaseUrl: string
  sessionToken: string | null
  currentTheme: ThemeName
  onPreviewTheme: (themeName: ThemeName) => void
  onSaveTheme: (themeName: ThemeName) => void
  onSettingsSaved: (settings: SettingsData) => void
  onClose: () => void
  onClearConversation: () => Promise<void>
}) {
  const panelRef = useRef<HTMLElement>(null)
  const closeButtonRef = useRef<HTMLButtonElement>(null)
  const [activeTab, setActiveTab] = useState<TabId>('voice')
  const [saved, setSaved] = useState<SettingsData | null>(null)
  const [draft, setDraft] = useState<SettingsData>(fallbackSettings)
  const [options, setOptions] = useState<SettingsOptions | null>(null)
  const [wakeInput, setWakeInput] = useState('')
  const [wakeError, setWakeError] = useState('')
  const [loadError, setLoadError] = useState('')
  const [saveError, setSaveError] = useState('')
  const [clearError, setClearError] = useState('')
  const [statusMessage, setStatusMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [clearing, setClearing] = useState(false)

  const dirty = useMemo(() => saved !== null && JSON.stringify(normalizeSettings(saved)) !== JSON.stringify(normalizeSettings(draft)), [draft, saved])
  const formError = draft.wake_words.length === 0 ? 'At least one wake word is required.' : wakeError
  const canSave = dirty && !formError && !saving && saved !== null

  const closePanel = useCallback(() => {
    if (saved) {
      setDraft(cloneSettings(saved))
      onPreviewTheme(saved.theme)
    }
    setWakeInput('')
    setWakeError('')
    setSaveError('')
    onClose()
  }, [onClose, onPreviewTheme, saved])

  useEffect(() => {
    if (!open) return
    let cancelled = false
    setLoading(true)
    setLoadError('')
    setSaveError('')
    setClearError('')
    setStatusMessage('')

    Promise.all([
      fetch(`${apiBaseUrl}/api/settings`),
      fetch(`${apiBaseUrl}/api/settings/options`),
    ])
      .then(async ([settingsResponse, optionsResponse]) => {
        if (!settingsResponse.ok) throw new Error(await readError(settingsResponse))
        if (!optionsResponse.ok) throw new Error(await readError(optionsResponse))
        const loaded = normalizeSettings((await settingsResponse.json()) as SettingsData)
        loaded.theme = normalizeThemeName(loaded.theme)
        const loadedOptions = (await optionsResponse.json()) as SettingsOptions
        if (cancelled) return
        setSaved(cloneSettings(loaded))
        setDraft(cloneSettings(loaded))
        setOptions(loadedOptions)
        onPreviewTheme(loaded.theme)
      })
      .catch((error: unknown) => {
        if (cancelled) return
        setSaved(null)
        setLoadError(parseErrorMessage(error))
        setDraft(current => ({ ...current, theme: currentTheme }))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [apiBaseUrl, onPreviewTheme, open])

  useEffect(() => {
    if (!open) return
    closeButtonRef.current?.focus()

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        closePanel()
        return
      }
      if (event.key !== 'Tab' || !panelRef.current) return

      const focusable = Array.from(
        panelRef.current.querySelectorAll<HTMLElement>(
          'button:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])',
        ),
      )
      if (focusable.length === 0) return
      const first = focusable[0]
      const last = focusable[focusable.length - 1]
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [closePanel, open])

  const setDraftValue = <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => {
    setDraft(current => ({ ...current, [key]: value }))
    setSaveError('')
    setStatusMessage('')
  }

  const addWakeWord = () => {
    const normalized = normalizeWakeWord(wakeInput)
    if (!normalized) {
      setWakeError('Enter a wake word first.')
      return
    }
    if (draft.wake_words.includes(normalized)) {
      setWakeError('This wake word already exists.')
      return
    }
    setDraftValue('wake_words', [...draft.wake_words, normalized])
    setWakeInput('')
    setWakeError('')
  }

  const removeWakeWord = (word: string) => {
    const next = draft.wake_words.filter(item => item !== word)
    setDraftValue('wake_words', next)
    setWakeError(next.length === 0 ? 'At least one wake word is required.' : '')
  }

  const saveChanges = async () => {
    if (!canSave || !sessionToken) {
      if (!sessionToken) setSaveError('Backend session is not ready. Reconnect and try again.')
      return
    }
    setSaving(true)
    setSaveError('')
    setStatusMessage('')
    try {
      const response = await fetch(`${apiBaseUrl}/api/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Locus-Session': sessionToken,
        },
        body: JSON.stringify(normalizeSettings(draft)),
      })
      if (!response.ok) throw new Error(await readError(response))
      const savedSettings = normalizeSettings((await response.json()) as SettingsData)
      savedSettings.theme = normalizeThemeName(savedSettings.theme)
      setSaved(cloneSettings(savedSettings))
      setDraft(cloneSettings(savedSettings))
      onSaveTheme(savedSettings.theme)
      onSettingsSaved(savedSettings)
      setStatusMessage('Settings saved.')
    } catch (error: unknown) {
      setSaveError(parseErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  const clearConversation = async () => {
    const confirmed = window.confirm('Clear the visible conversation history? This will not delete the model, API keys, or settings.')
    if (!confirmed) return
    setClearing(true)
    setClearError('')
    try {
      await onClearConversation()
      setStatusMessage('Conversation history cleared.')
    } catch (error: unknown) {
      setClearError(parseErrorMessage(error))
    } finally {
      setClearing(false)
    }
  }

  if (!open) return null

  return (
    <div className="settings-layer" aria-hidden={!open}>
      <button
        type="button"
        className="settings-backdrop"
        aria-label="Close settings"
        onClick={() => {
          if (!dirty) closePanel()
        }}
      />
      <section
        ref={panelRef}
        className="settings-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="settings-title"
        style={{
          '--settings-bg': theme.sidebar,
          '--settings-panel': theme.panelBg,
          '--settings-border': theme.panelBorder,
          '--settings-text': theme.text,
          '--settings-muted': theme.subtext,
          '--settings-accent': theme.accent,
          '--settings-accent-text': theme.accentText,
          '--settings-input': theme.inputBg,
          '--settings-button-text': theme.listenBtnText,
        } as CSSProperties}
      >
        <header className="settings-header">
          <div>
            <h2 id="settings-title">Settings</h2>
            <p>Configure Locus AI behaviour and appearance</p>
          </div>
          <button ref={closeButtonRef} type="button" className="icon-button" aria-label="Close settings" onClick={closePanel}>
            x
          </button>
        </header>

        <div className="settings-tabs" role="tablist" aria-label="Settings sections">
          {tabs.map(tab => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={activeTab === tab.id}
              className={activeTab === tab.id ? 'settings-tab active' : 'settings-tab'}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="settings-content">
          {loading && <p className="settings-note">Loading settings...</p>}
          {loadError && (
            <div className="settings-error" role="alert">
              Settings could not be loaded: {loadError}
            </div>
          )}

          {!loading && activeTab === 'voice' && (
            <VoiceWakeTab
              draft={draft}
              options={options}
              wakeInput={wakeInput}
              wakeError={formError}
              setWakeInput={setWakeInput}
              addWakeWord={addWakeWord}
              removeWakeWord={removeWakeWord}
              setDraftValue={setDraftValue}
            />
          )}

          {!loading && activeTab === 'ai' && (
            <AiModelTab
              draft={draft}
              options={options}
              setAiModel={(model) => setDraftValue('ai_model', model)}
            />
          )}

          {!loading && activeTab === 'appearance' && (
            <AppearanceTab
              draft={draft}
              setTheme={(themeName) => {
                setDraftValue('theme', themeName)
                onPreviewTheme(themeName)
              }}
            />
          )}

          {!loading && activeTab === 'advanced' && (
            <AdvancedTab
              draft={draft}
              clearError={clearError}
              clearing={clearing}
              setDraftValue={setDraftValue}
              clearConversation={clearConversation}
            />
          )}
        </div>

        <footer className="settings-footer">
          <div aria-live="polite">
            {saveError && <span className="settings-error inline">{saveError}</span>}
            {statusMessage && <span className="settings-success">{statusMessage}</span>}
          </div>
          <button type="button" className="secondary-button" onClick={closePanel}>
            Cancel
          </button>
          <button type="button" className="primary-button" disabled={!canSave || !sessionToken} onClick={() => void saveChanges()}>
            {saving ? 'Saving...' : 'Save changes'}
          </button>
        </footer>
      </section>
    </div>
  )
}

function VoiceWakeTab({
  draft,
  options,
  wakeInput,
  wakeError,
  setWakeInput,
  addWakeWord,
  removeWakeWord,
  setDraftValue,
}: {
  draft: SettingsData
  options: SettingsOptions | null
  wakeInput: string
  wakeError: string
  setWakeInput: (value: string) => void
  addWakeWord: () => void
  removeWakeWord: (word: string) => void
  setDraftValue: <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => void
}) {
  const languages = options?.languages ?? {}
  return (
    <div className="settings-stack">
      <FieldGroup label="Wake words">
        <div className="chip-row">
          {draft.wake_words.map(word => (
            <button key={word} type="button" className="wake-chip" onClick={() => removeWakeWord(word)} aria-label={`Remove ${word}`}>
              {word} <span aria-hidden="true">x</span>
            </button>
          ))}
        </div>
        <div className="inline-row">
          <input
            value={wakeInput}
            onChange={(event) => setWakeInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                event.preventDefault()
                addWakeWord()
              }
            }}
            placeholder="Add wake word..."
            aria-label="Add wake word"
          />
          <button type="button" className="primary-button compact" onClick={addWakeWord}>
            Add
          </button>
        </div>
        {wakeError && <p className="settings-error">{wakeError}</p>}
      </FieldGroup>

      <FieldGroup label="Microphone sensitivity">
        <div className="slider-row">
          <input
            type="range"
            min={0}
            max={100}
            value={draft.microphone_sensitivity}
            aria-label="Microphone sensitivity"
            onChange={(event) => setDraftValue('microphone_sensitivity', Number(event.target.value))}
          />
          <strong>{draft.microphone_sensitivity}%</strong>
        </div>
        <p className="settings-note">Higher values pick up softer sounds and may cause false triggers.</p>
      </FieldGroup>

      <FieldGroup label="Language">
        <select
          value={draft.language_code}
          aria-label="Language"
          onChange={(event) => setDraftValue('language_code', event.target.value)}
        >
          {Object.entries(languages).map(([code, meta]) => (
            <option key={code} value={code}>{meta.label}</option>
          ))}
        </select>
      </FieldGroup>

      <FieldGroup label="TTS voice">
        <select value={draft.tts_voice} disabled aria-label="TTS voice">
          <option value="">Unavailable</option>
        </select>
        <p className="settings-note">{options?.tts_voice_unavailable_reason ?? 'Text-to-speech voice selection is unavailable.'}</p>
      </FieldGroup>

      <ToggleRow
        label="Auto-listen on startup"
        description="Start wake-word listening when the app opens. Applies on next startup."
        checked={draft.auto_listen_on_startup}
        onChange={(checked) => setDraftValue('auto_listen_on_startup', checked)}
      />
      <ToggleRow
        label="Show live transcript"
        description="Display recognized speech in the conversation panel."
        checked={draft.show_live_transcript}
        onChange={(checked) => setDraftValue('show_live_transcript', checked)}
      />
    </div>
  )
}

function AiModelTab({
  draft,
  options,
  setAiModel,
}: {
  draft: SettingsData
  options: SettingsOptions | null
  setAiModel: (model: AiModel) => void
}) {
  const aiModels = options?.ai_models ?? {}
  return (
    <div className="settings-stack">
      {(['local', 'gemini', 'openai'] as const).map(model => {
        const meta = aiModels[model]
        const disabled = model === 'openai' || Boolean(meta?.disabled) || (model === 'gemini' && meta?.requires_api_key && !meta.configured)
        return (
          <label key={model} className={draft.ai_model === model ? 'radio-card active' : 'radio-card'}>
            <input
              type="radio"
              name="ai-model"
              value={model}
              checked={draft.ai_model === model}
              disabled={disabled}
              onChange={() => {
                if (model !== 'openai') setAiModel(model)
              }}
            />
            <span>
              <strong>{meta?.label ?? model}</strong>
              <small>{disabled ? meta?.reason ?? 'Requires a configured API key.' : meta?.description}</small>
            </span>
          </label>
        )
      })}
    </div>
  )
}

function AppearanceTab({ draft, setTheme }: { draft: SettingsData; setTheme: (themeName: ThemeName) => void }) {
  return (
    <div className="theme-grid">
      {themeOrder.map(themeName => {
        const option = themes[themeName]
        return (
          <button
            key={themeName}
            type="button"
            className={draft.theme === themeName ? 'theme-card active' : 'theme-card'}
            onClick={() => setTheme(themeName)}
            aria-pressed={draft.theme === themeName}
          >
            <span style={{ background: option.accent }} />
            <strong>{option.label}</strong>
          </button>
        )
      })}
    </div>
  )
}

function AdvancedTab({
  draft,
  clearError,
  clearing,
  setDraftValue,
  clearConversation,
}: {
  draft: SettingsData
  clearError: string
  clearing: boolean
  setDraftValue: <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => void
  clearConversation: () => Promise<void>
}) {
  return (
    <div className="settings-stack">
      <ToggleRow
        label="Debug mode"
        description="Enable internal debug logging without exposing secrets."
        checked={draft.debug_mode}
        onChange={(checked) => setDraftValue('debug_mode', checked)}
      />
      <ToggleRow
        label="Local intent cache"
        description="Keep trained local intent artifacts for faster startup."
        checked={draft.local_intent_cache}
        onChange={(checked) => setDraftValue('local_intent_cache', checked)}
      />
      <FieldGroup label="Clear data">
        <button type="button" className="danger-button" disabled={clearing} onClick={() => void clearConversation()}>
          {clearing ? 'Clearing...' : 'Clear conversation history'}
        </button>
        {clearError && <p className="settings-error">{clearError}</p>}
      </FieldGroup>
    </div>
  )
}

function FieldGroup({ label, children }: { label: string; children: ReactNode }) {
  return (
    <section className="field-group">
      <h3>{label}</h3>
      {children}
    </section>
  )
}

function ToggleRow({
  label,
  description,
  checked,
  onChange,
}: {
  label: string
  description: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  return (
    <label className="toggle-row">
      <span>
        <strong>{label}</strong>
        <small>{description}</small>
      </span>
      <input type="checkbox" checked={checked} onChange={(event) => onChange(event.target.checked)} />
    </label>
  )
}
