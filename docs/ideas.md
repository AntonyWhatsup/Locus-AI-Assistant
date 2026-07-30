# Ideas

## Documentation Purpose

This file collects possible future improvements for Locus. It is intentionally separate from the confirmed feature set in `FEATURES.md`.

## Voice And Conversation

- Allow users to configure their own wake word
- Improve speech recognition accuracy and accent handling
- Add multi-turn dialogue with remembered context
- Improve Gemini prompt handling for better question answering

## AI And Language

- Expand `src/brain/intents.json` with more commands and examples
- Add multi-language recognition and responses
- Explore online or incremental model adaptation
- Detect sentiment or tone to adjust responses

## Actions And Integrations

- Add reminders and calendar-related commands
- Add media playback controls
- Add system-level commands such as opening files or taking screenshots
- Add smart-home device integration
- Support user-defined custom actions or scripts

## UI And UX

- Improve the listening visualizer
- Add appearance themes or avatar customization
- Add user notifications for command results
- Add an interaction history panel

## Engineering

- Reduce startup and processing overhead
- Add a plugin-style extension model
- Expand unit and integration test coverage
- Keep React/PyWebView UI integration small enough that backend runtime state remains easy to test
