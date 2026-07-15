# Cat Meme Theme — "Nyan" Mode

## Context

The user's assistant is inspired by cat memes (the cat photo in the AssistantPanel, meme-y status messages like "Go ahead"). They want a 5th theme that feels **uniquely cat-internet** — distinct from the existing 4 utilitarian themes. The goal is something fun and memorable that leans into the meme identity of the assistant.

## Chosen direction: Vaporwave Cat — "Nyan"

A **hot pink + cyan + deep purple** vaporwave aesthetic — the visual language of early internet meme culture (think Nyan Cat, retro grid, glowing text). Panels are frosted glass over a CSS-generated retro scene (no external image needed). This is the most distinctive and thematically on-brand choice.

---

## Implementation Plan

### 1. `src/themes.ts`
- Add `'cat'` to the `ThemeName` union
- Add a `cat` theme entry:
  - `bg`: `'transparent'` (custom background in App.tsx)
  - `panelBg`: `'rgba(30,0,40,0.45)'` — dark purple glass
  - `panelBorder`: `'rgba(255,45,160,0.25)'` — hot pink
  - `sidebar`: `'rgba(20,0,30,0.55)'`
  - `sidebarAccent`: `'#ff2d78'` — hot pink
  - `accent`: `'#ff2d78'`
  - `accentDim`: `'rgba(255,45,120,0.18)'`
  - `accentText`: `'#ff6eb4'`
  - `text`: `'#ffe8f8'`
  - `subtext`: `'#9b6aaa'`
  - `inputBg`: `'rgba(255,45,120,0.07)'`
  - `listenBtn`: `'#ff2d78'`
  - `listenBtnText`: `'#1a0020'`
  - `statusBadge`: `'rgba(255,45,120,0.2)'`
  - `statusText`: `'#ff6eb4'`
  - `label`: `'Nyan'`

### 2. `src/App.tsx`
Add a CSS-only vaporwave background for the `'cat'` theme (no image needed, pure CSS):
- `background` condition extended: also `'transparent'` when `themeName === 'cat'`
- Add a `{themeName === 'cat' && ...}` background block containing:
  - **Base**: deep purple-to-black radial gradient (`#0d0018` → `#1a0030`)
  - **Retro perspective grid** (bottom half): CSS `linear-gradient` lines in magenta at low opacity, using `perspective` transform skewed to the bottom
  - **Ambient glow blobs**: hot pink top-center blob + cyan bottom-left blob (matching the glass-green pattern)
  - **Star field**: small white dots (pure CSS, no image)

The retro grid can be achieved with:
```css
backgroundImage: 'linear-gradient(rgba(255,45,160,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(255,45,160,0.3) 1px, transparent 1px)'
backgroundSize: '60px 60px'
transform: 'perspective(300px) rotateX(60deg)'
```

### 3. `src/components/TopBar.tsx`
- Add `'cat'` to `themeOrder` array and `themeLabels` map with label `"Nyan"`

### 4. `src/components/AssistantPanel.tsx` (optional enhancement)
- When `theme.name === 'cat'`, change the `catMessages` to meme text:
  - `idle`: `'can i haz?'`
  - `listening`: `'im listenin'`
  - `thinking`: `'...big thonk'`
  - `speaking`: `'meow meow'`

  This can be done by passing `theme.name` into the component and using a secondary messages map.

---

## Files to modify

| File | Change |
|------|--------|
| `src/themes.ts` | Add `'cat'` to `ThemeName`, add `cat` theme object |
| `src/App.tsx` | Add `cat` to transparent-bg condition, add CSS vaporwave background block |
| `src/components/TopBar.tsx` | Add `'cat'` to `themeOrder` and `themeLabels` |
| `src/components/AssistantPanel.tsx` | Optional: meme cat status messages when theme is `cat` |

---

## Verification

1. Switch to "Nyan" theme via the theme switcher in the top bar
2. Confirm retro grid + pink/cyan glow blobs render in the background
3. Confirm all panels appear as dark purple frosted glass with pink borders
4. Confirm sidebar accent bar and status dot are hot pink
5. Confirm Listen button is hot pink
6. Confirm cat status messages show meme text (idle: "can i haz?")
7. Switch between all 5 themes to confirm no regressions in other themes
