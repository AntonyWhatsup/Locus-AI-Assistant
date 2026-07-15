# UI Rebuild From ZIP Report

## Summary

This project should not merely borrow visual ideas from `Assistant UI Design.zip`. The current desktop UI should be rewritten to match that design as closely as the Tkinter stack allows.

The ZIP is the visual source of truth. The current Python/Tkinter application remains the runtime and behavior source of truth.

That means:

- the UI layout, hierarchy, panel structure, spacing, and theme behavior should be rebuilt around the ZIP design
- the current assistant logic, settings behavior, wake-word flow, Gemini integration, and cat-state transitions must continue to work
- the rebuild must be done natively in Tkinter rather than by embedding the web prototype

## Source vs Target

### Source Design

The ZIP contains a web prototype built with:

- React
- Vite
- TypeScript
- CSS animation and browser layout primitives

Primary source files inside the ZIP:

- `src/App.tsx`
- `src/themes.ts`
- `src/components/TopBar.tsx`
- `src/components/Sidebar.tsx`
- `src/components/AssistantPanel.tsx`
- `src/components/VoicePanel.tsx`
- `src/components/ConversationPanel.tsx`
- `src/components/SessionPanel.tsx`
- `src/index.css`

### Target Application

The live app is a desktop application built with:

- Tkinter
- PIL/ImageTk
- Python runtime state and callbacks

Primary implementation target:

- `src/ui_manager.py`

Supporting runtime modules that must remain compatible:

- `main.py`
- `src/processor.py`
- `src/actions.py`
- `src/settings_manager.py`

### Implication

There is no direct code reuse path from the React UI into the Tkinter app. The correct approach is a native Tkinter reimplementation of the ZIP design, while preserving current backend behavior.

## Rebuild Goal

The current UI should be restructured so the desktop application visually and structurally mirrors the ZIP design:

- left sidebar navigation rail
- top header with title, search area, theme switcher, and status badge
- 2x2 dashboard layout
- assistant panel
- voice activity panel
- conversation panel
- session summary panel
- theme-driven visual styling close to the ZIP variants

This is a UI rewrite, not a minor reskin.

## What Must Match The ZIP Design

### Overall Layout

- the main shell should follow the ZIP dashboard composition
- the sidebar must be a persistent left rail
- the top bar must act as a unified header rather than a loose collection of controls
- the main body must present four core dashboard panels with the same role breakdown as the ZIP

### Panel Structure

- `Assistant` panel should match the ZIP composition:
  - cat image area
  - overlay status text on the image
  - control deck column
  - primary and secondary action buttons
  - readiness/status chips
- `Voice` panel should match the ZIP structure:
  - status headline
  - status subcopy
  - live/passive indicator
  - animated waveform region
  - secondary bar strip or historical visual area
- `Conversation` panel should be a stacked, scrollable conversation area instead of the current fixed two-message presentation
- `Session Summary` panel should use row-based summary blocks that follow the ZIP visual treatment

### Header And Navigation

- the top bar should mirror the ZIP composition:
  - app title and subtitle on the left
  - search field region
  - theme switcher group
  - compact status badge
- the sidebar should mirror the ZIP grouping and emphasis:
  - narrow rail layout
  - icon-led navigation items
  - visual active state
  - footer item placement

### Theme Behavior

- the theme system should be rebuilt to match the ZIP token intent more closely
- `glass green`, `dark`, `light`, and `colorful` should remain supported
- visual contrast, accent usage, muted text, panel backgrounds, and chip treatments should follow the ZIP hierarchy

## What Must Stay From The Current App

- manual click-to-listen behavior
- wake-word activation flow
- Gemini fallback behavior
- settings dialog and settings persistence behavior
- cat-state image transitions
- live microphone-driven visualization where app state supports it
- current startup/training/listening flow
- all current button actions, even if their placement and styling change

The rebuild is allowed to move controls, rename visible labels, and reorganize regions, but it must not silently drop existing working features.

## What Cannot Be Reused Directly

- React component code
- JSX layout code
- browser CSS effects such as `backdrop-filter`
- Tailwind/web scrollbar behavior
- HTML input and flex/grid behavior as code
- placeholder demo data that has no equivalent in the current application
- remote image/background behavior that depends on browser layering

These parts should be translated, not copied.

## How Non-Reusable Web Parts Will Be Rewritten

### React Component Structure

- ZIP source:
  - React components such as `TopBar.tsx`, `Sidebar.tsx`, `AssistantPanel.tsx`, `VoicePanel.tsx`, `ConversationPanel.tsx`, and `SessionPanel.tsx`
- Why it cannot be reused directly:
  - the current app is not a React runtime and does not render JSX components
- Tkinter rewrite strategy:
  - rewrite each component as a Tkinter builder section or helper owned by `LocusUI`
  - prefer explicit builder methods such as `_build_top_bar()`, `_build_sidebar()`, `_build_assistant_panel()`, `_build_voice_panel()`, `_build_conversation_panel()`, and `_build_session_panel()`
- Destination:
  - `src/ui_manager.py`
- Acceptance expectation:
  - the Tkinter widget hierarchy mirrors the ZIP component hierarchy even though the implementation is Python/Tkinter

### JSX Composition And Prop-Driven Rendering

- ZIP source:
  - prop-based rendering and state-driven React rerenders
- Why it cannot be reused directly:
  - Tkinter uses persistent widgets and explicit update calls, not declarative rerendering
- Tkinter rewrite strategy:
  - convert prop/state updates into instance attributes plus update methods
  - continue driving runtime UI changes through methods such as `set_status()`, `set_transcript()`, `fade_to_image()`, `set_mic_state()`, and `update_mic_level()`
- Destination:
  - `src/ui_manager.py`
  - runtime event sources remain in `src/processor.py` and `src/actions.py`
- Acceptance expectation:
  - all visible state changes still propagate immediately, but through Tkinter callbacks and widget mutation instead of rerender

### CSS Flex/Grid Layout

- ZIP source:
  - browser flexbox and grid layout in `src/App.tsx` and panel components
- Why it cannot be reused directly:
  - Tkinter does not support CSS layout primitives
- Tkinter rewrite strategy:
  - rebuild the dashboard with explicit `pack`/`grid` containers
  - use row and column weights to preserve the ZIP shell hierarchy and resize behavior
  - match the ZIP structure first, then tune spacing and proportions within desktop constraints
- Destination:
  - `LocusUI._build_layout()` and panel builder helpers in `src/ui_manager.py`
- Acceptance expectation:
  - the app uses the same sidebar/header/2x2 dashboard composition as the ZIP and resizes predictably on desktop

### Glass, Blur, And Ambient CSS Effects

- ZIP source:
  - `backdrop-filter`, translucent glass panels, layered ambient glow, and web-style overlays
- Why it cannot be reused directly:
  - Tkinter does not provide browser blur or CSS compositing
- Tkinter rewrite strategy:
  - approximate the effect using layered frames, contrast borders, muted panel backgrounds, local background imagery, and stronger theme token control
  - treat the effect as visual approximation, not literal parity
- Destination:
  - theme tokens and panel styling inside `src/ui_manager.py`
  - any new decorative assets should live in `assets/`
- Acceptance expectation:
  - the rebuilt UI feels visually close to the ZIP's glass treatment without relying on browser-only blur features

### CSS Animations

- ZIP source:
  - CSS keyframes for waveform bars and pulse dots in `src/index.css`
- Why it cannot be reused directly:
  - Tkinter does not run CSS animations
- Tkinter rewrite strategy:
  - translate them into `after(...)` timer loops
  - extend existing animation infrastructure such as `fade_to_image()`, `_start_bar_loop()`, and mic-canvas redraw behavior
  - add small helper loops for badge pulse or decorative waveform cycling if needed
- Destination:
  - `src/ui_manager.py`
  - state triggers remain sourced from `src/processor.py`
- Acceptance expectation:
  - waveform, pulse, and status motion communicate the same state transitions as the ZIP using native Tkinter timing

### Scrollbars And Overflow Behavior

- ZIP source:
  - browser overflow scrolling in the conversation panel and app shell
- Why it cannot be reused directly:
  - Tkinter scroll behavior must be explicitly built
- Tkinter rewrite strategy:
  - use `Canvas` + embedded `Frame` + `Scrollbar`
  - reuse the same scrolling pattern already introduced in the settings dialog for any tall or dynamic content areas
- Destination:
  - `src/ui_manager.py`
- Acceptance expectation:
  - conversation, settings, and any long dashboard regions remain reachable without content clipping

### HTML Inputs And Search Controls

- ZIP source:
  - HTML inputs, buttons, and grouped search control styling
- Why it cannot be reused directly:
  - Tkinter uses different control widgets and state handling
- Tkinter rewrite strategy:
  - rebuild them with `Entry`, `Button`, `ttk.Combobox`, and styled wrapper frames
  - if the ZIP search box remains visual-only in this phase, label it internally as a shell element and do not imply full search behavior
- Destination:
  - `src/ui_manager.py`
  - settings behavior remains connected to `src/settings_manager.py`
- Acceptance expectation:
  - controls match the ZIP structure visually while retaining current desktop behavior and avoiding fake functionality claims

### Icons And SVG Graphics

- ZIP source:
  - inline SVG icons in sidebar and header controls
- Why it cannot be reused directly:
  - Tkinter does not render React inline SVG markup as widgets
- Tkinter rewrite strategy:
  - default to simple local raster assets or text/canvas-drawn icons
  - use text/canvas icons first for speed, then swap to exported local assets if more visual fidelity is needed
- Destination:
  - `src/ui_manager.py`
  - optional local icon assets in `assets/`
- Acceptance expectation:
  - sidebar and header retain the ZIP icon-led navigation feel without adding a new rendering dependency

### Remote Images And Browser Layered Backgrounds

- ZIP source:
  - remote web images and browser overlay layering
- Why it cannot be reused directly:
  - the desktop app should not depend on remote design assets for core rendering
- Tkinter rewrite strategy:
  - use existing local cat assets as the functional baseline
  - export any new decorative backgrounds or icons into local project assets if they are needed to improve parity
  - avoid network-loaded visual dependencies
- Destination:
  - `assets/`
  - image loading and placement in `src/ui_manager.py`
- Acceptance expectation:
  - the rebuilt UI is visually consistent and locally self-contained

### Demo-Only Session And Conversation Data

- ZIP source:
  - placeholder messages, fake session metrics, and demo-only values
- Why it cannot be reused directly:
  - the current app must show real application state wherever possible
- Tkinter rewrite strategy:
  - bind conversation and session summary views to real current runtime data first
  - if a ZIP metric has no backend source yet, either remove it or keep it as an explicit temporary placeholder during staged implementation
- Destination:
  - display logic in `src/ui_manager.py`
  - runtime sources in `src/processor.py`, `src/actions.py`, `src/config.py`, and settings/state accessors
- Acceptance expectation:
  - the rebuilt dashboard looks like the ZIP but does not present fake live information as if it were real

### Theme Token System

- ZIP source:
  - `src/themes.ts` token-based theme definition
- Why it cannot be reused directly:
  - the TypeScript theme object is not directly consumable by Tkinter and does not match all current token names
- Tkinter rewrite strategy:
  - normalize the Tkinter `THEMES` structure into a stable internal token contract
  - ensure all rebuilt panels use shared tokens for background, panel, border, title, text, muted copy, accent, chip, input, and motion-related colors
- Destination:
  - `src/ui_manager.py`
- Acceptance expectation:
  - themes switch consistently across the whole rebuilt app and reflect the ZIP's visual intent with one styling source of truth

## Explicit Mapping To The Current Project

- `src/themes.ts` -> rebuild and normalize the Tkinter `THEMES` dictionary in `src/ui_manager.py`
- `src/components/TopBar.tsx` -> rewrite the current Tkinter `top_bar`
- `src/components/Sidebar.tsx` -> rebuild the current `rail_card`, `rail_nav`, and footer area
- `src/components/AssistantPanel.tsx` -> rewrite the current `hero_card`
- `src/components/VoicePanel.tsx` -> rewrite the current `mic_card`
- `src/components/ConversationPanel.tsx` -> replace the current fixed transcript card structure with a scrollable stacked conversation panel
- `src/components/SessionPanel.tsx` -> rewrite the current `control_card`
- `src/index.css` animation ideas -> translate waveform and pulse patterns into Tkinter canvas/timed updates
- `src/App.tsx` -> overall shell/layout reference for `LocusUI._build_layout()`

## Planned Changes

### 1. Treat The ZIP As The UI Specification

- use the ZIP layout and component roles as the target structure
- stop treating the current `LocusUI` arrangement as the layout to preserve
- preserve behavior, not the current screen organization

### 2. Refactor `src/ui_manager.py` Before Final Styling

- split the UI construction into clearer panel-builder sections that mirror the ZIP component boundaries
- keep `LocusUI` as the main owner, but make the shell easier to rewrite without mixing all layout logic together
- separate shell, header, sidebar, assistant panel, voice panel, conversation panel, session panel, and settings window builders

### 3. Define Tkinter Replacements For Non-Reusable Web Mechanisms

- document the native rewrite for component structure, layout, animation, icons, scroll handling, backgrounds, and control widgets before final visual assembly
- use this translation layer as the implementation checklist for all web-only ZIP behaviors
- keep the replacement mechanisms centered in `src/ui_manager.py`, with runtime state still sourced from the existing Python modules

### 4. Rebuild The Main Shell

- rewrite the desktop shell so the default screen uses:
  - left sidebar rail
  - top header
  - two-by-two dashboard grid
- keep window sizing and resize behavior compatible with Tkinter desktop constraints
- preserve current theme switching and runtime status updates while restyling them to match the ZIP

### 5. Rebuild The Assistant Panel

- keep the clickable cat image as the primary interaction anchor
- restyle the image region to match the ZIP card composition
- move the current control deck content into a ZIP-style side column
- preserve the existing `Listen` and `Settings` actions
- keep readiness chips, but restyle and simplify them to match the ZIP visual language

### 6. Rebuild The Voice Panel

- keep the real microphone-driven visualization path
- restructure the panel to follow the ZIP headline/subcopy/live-passive layout
- translate the ZIP waveform animation concept into Tkinter canvas or timed bar widgets
- preserve current listening/thinking/idle runtime states and expose them with ZIP-like labels

### 7. Rebuild The Conversation Panel

- replace the current fixed two-card transcript area with a stacked scrollable conversation view
- keep `You` and `Locus` message roles
- support longer session histories inside the panel
- keep live updates driven by current assistant events

### 8. Rebuild The Session Summary Panel

- convert the current summary area to ZIP-style row blocks
- populate rows with real data first:
  - current Gemini model
  - wake words
  - interaction/help text
  - runtime/session stats only if they can be backed by real data
- avoid fake metrics unless clearly marked as placeholders during development

### 9. Rebuild Header And Sidebar

- header should visually match the ZIP:
  - tighter grouping
  - clearer status chip
  - theme control group
  - search-like field treatment
- sidebar should use icon-led navigation and a stronger active-state system
- if some nav items are not functional yet, they may remain visual placeholders, but they should not misrepresent actual navigation behavior

### 10. Align The Settings Window After The Shell Rebuild

- restyle the settings dialog to match the rebuilt design system
- keep current scrolling, validation, and persistence behavior
- preserve Gemini key/model, voice, audio device, and appearance settings functionality

### 11. Final Polish Pass

- tune spacing, borders, colors, and typography against the ZIP reference
- verify resizing behavior for desktop window sizes
- ensure scrollable regions behave correctly
- ensure theme parity across all supported themes

## Recommended Rebuild Strategy

The recommended approach is a native Tkinter rebuild.

Reasons:

- the current app is already fully wired around Tkinter
- embedding the web prototype would introduce a second UI runtime and duplicate state wiring
- the ZIP's highest value is its visual composition and component structure, not reusable business logic
- a Tkinter-native rebuild keeps the app architecture coherent

The rebuild should therefore be treated as:

- ZIP design as visual specification
- current Python app as behavior specification
- `src/ui_manager.py` as the primary rewrite target

## Step-By-Step Implementation Order

1. Freeze existing functional behaviors that must survive the redesign.
2. Document the ZIP component-to-Tkinter mapping and keep it as the rewrite checklist.
3. Define the Tkinter-native replacement for each non-reusable web mechanism.
4. Refactor `src/ui_manager.py` into clearer builder methods aligned to ZIP component boundaries.
5. Rebuild the shell layout to match the ZIP dashboard structure.
6. Rebuild the header and sidebar.
7. Rebuild the assistant panel around the ZIP composition.
8. Rebuild the voice activity panel around the ZIP structure while preserving real runtime state.
9. Rebuild the conversation panel into a scrollable stacked message view.
10. Rebuild the session summary panel around real app data.
11. Restyle the settings dialog to fit the rebuilt design system.
12. Run a final resize, theme, and interaction polish pass.

## Acceptance Criteria For The Rebuild

- the live Tkinter app matches the ZIP design in layout and visual hierarchy as closely as the stack allows
- the rebuild is visibly a redesign/rewrite, not a mild restyle
- the app still supports current assistant functionality
- the main dashboard uses the same panel roles as the ZIP
- the conversation area supports scrollable stacked messages
- the theme system reflects the ZIP visual intent
- `src/ui_manager.py` is reorganized enough to support ongoing UI iteration cleanly

## Conclusion

The correct path is to rewrite the current app UI to match the ZIP design natively in Tkinter. The ZIP should be treated as the design specification, while the current project code remains the behavior and integration foundation.

This should be executed as a substantial UI rebuild, not as incremental cosmetic tweaking.
