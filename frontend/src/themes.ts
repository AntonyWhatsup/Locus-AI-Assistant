export type ThemeName = 'glass-green' | 'dark' | 'light' | 'colorful' | 'cat'

export interface Theme {
  name: ThemeName
  label: string
  bg: string
  panelBg: string
  panelBorder: string
  sidebar: string
  sidebarAccent: string
  accent: string
  accentDim: string
  accentText: string
  text: string
  subtext: string
  inputBg: string
  listenBtn: string
  listenBtnText: string
  statusBadge: string
  statusText: string
}

export const themes: Record<ThemeName, Theme> = {
  'glass-green': {
    name: 'glass-green',
    label: 'Glass Green',
    bg: 'transparent',
    panelBg: 'rgba(8,30,16,0.38)',
    panelBorder: 'rgba(0,255,120,0.18)',
    sidebar: 'rgba(4,18,8,0.45)',
    sidebarAccent: '#00ff7f',
    accent: '#00e87a',
    accentDim: 'rgba(0,232,122,0.18)',
    accentText: '#00e87a',
    text: '#d8f5e5',
    subtext: '#9bc5a9',
    inputBg: 'rgba(0,255,80,0.06)',
    listenBtn: '#00e87a',
    listenBtnText: '#021208',
    statusBadge: 'rgba(0,232,122,0.18)',
    statusText: '#00e87a',
  },
  dark: {
    name: 'dark',
    label: 'Dark',
    bg: '#11151c',
    panelBg: 'rgba(20,26,35,0.95)',
    panelBorder: 'rgba(255,255,255,0.06)',
    sidebar: '#0c1017',
    sidebarAccent: '#22c55e',
    accent: '#22c55e',
    accentDim: 'rgba(34,197,94,0.12)',
    accentText: '#22c55e',
    text: '#e8eaf0',
    subtext: '#5a6478',
    inputBg: 'rgba(255,255,255,0.04)',
    listenBtn: '#22c55e',
    listenBtnText: '#030b05',
    statusBadge: 'rgba(34,197,94,0.15)',
    statusText: '#22c55e',
  },
  light: {
    name: 'light',
    label: 'Light',
    bg: '#f0f4f0',
    panelBg: '#ffffff',
    panelBorder: 'rgba(0,0,0,0.07)',
    sidebar: '#ffffff',
    sidebarAccent: '#16a34a',
    accent: '#16a34a',
    accentDim: 'rgba(22,163,74,0.08)',
    accentText: '#16a34a',
    text: '#111827',
    subtext: '#6b7280',
    inputBg: '#f3f4f6',
    listenBtn: '#16a34a',
    listenBtnText: '#ffffff',
    statusBadge: 'rgba(22,163,74,0.1)',
    statusText: '#16a34a',
  },
  colorful: {
    name: 'colorful',
    label: 'Colorful',
    bg: '#100820',
    panelBg: 'rgba(28,16,50,0.9)',
    panelBorder: 'rgba(249,115,22,0.15)',
    sidebar: '#0e0620',
    sidebarAccent: '#f97316',
    accent: '#f97316',
    accentDim: 'rgba(249,115,22,0.15)',
    accentText: '#f97316',
    text: '#f0eaff',
    subtext: '#8b7aab',
    inputBg: 'rgba(80,50,120,0.2)',
    listenBtn: '#f97316',
    listenBtnText: '#1a0820',
    statusBadge: 'rgba(249,115,22,0.2)',
    statusText: '#f97316',
  },
  cat: {
    name: 'cat',
    label: 'Nyan',
    bg: 'transparent',
    panelBg: 'rgba(30,0,40,0.45)',
    panelBorder: 'rgba(255,45,160,0.25)',
    sidebar: 'rgba(20,0,30,0.55)',
    sidebarAccent: '#ff2d78',
    accent: '#ff2d78',
    accentDim: 'rgba(255,45,120,0.18)',
    accentText: '#ff6eb4',
    text: '#ffe8f8',
    subtext: '#9b6aaa',
    inputBg: 'rgba(255,45,120,0.07)',
    listenBtn: '#ff2d78',
    listenBtnText: '#1a0020',
    statusBadge: 'rgba(255,45,120,0.2)',
    statusText: '#ff6eb4',
  },
}
