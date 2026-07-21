# Locus AI Assistant

Locus is a Windows desktop voice assistant built with Python, FastAPI, PyWebView, React, PyTorch, MCP, and Google Gemini. It combines a small offline intent classifier with optional cloud integrations and a cat-themed UI.

## Documentation Map

- [User Guide](docs/USER_GUIDE.md): how to run and use the assistant
- [Technical Information](docs/TECHNICAL_INFO.md): architecture, modules, and runtime flow
- [Features](docs/FEATURES.md): current capabilities and status
- [Ideas](docs/ideas.md): future improvements and expansion ideas

## Project Summary

- Manual click-to-listen activation with optional cloud wake-word mode
- Offline intent recognition backed by a small neural network
- Optional Gemini responses for unsupported or conversational queries
- Chrome and YouTube launch flows with per-profile selection
- Optional MCP stdio tool calls through a bundled sample server
- React UI served by the local FastAPI backend inside a PyWebView window

## Project Structure

```text
Locus_AI_Assistant/
|-- main.py
|-- requirements.txt
|-- assets/
|-- data/
|-- docs/
|-- frontend/
|-- logs/
|-- scripts/
|-- src/
`-- tests/
```

## Quick Start

1. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

2. Install Python dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Install and build the frontend:

   ```powershell
   cd frontend
   npm install
   npm run build
   cd ..
   ```

4. Create a `.env` file in the project root:

   ```env
   GEMINI_KEY=your_google_gemini_api_key_here
   ```

5. Optional: enable cloud features. By default these are disabled so ambient audio and unsupported dictated text are not sent to cloud services automatically.

   ```env
   LOCUS_ENABLE_CLOUD_WAKE_LISTENER=1
   LOCUS_ENABLE_GEMINI_FALLBACK=1
   ```

6. Run the app:

   ```powershell
   python main.py
   ```

## MCP Quick Start

Locus can call a configured MCP server over stdio.

1. Enable MCP in `data/settings.json` through the UI or by writing:

   ```json
   {
     "mcp_enabled": true,
     "mcp_server_command": "python scripts/mcp_project_server.py",
     "mcp_default_tool": "answer_project_question"
   }
   ```

2. Start Locus and say `project status` to trigger the bundled `project_status` tool.

3. With the sample server configured, low-confidence requests can route into the default MCP tool before optional Gemini fallback.

## Verification

```powershell
python -B -m unittest discover -s tests
```

## Notes

- The model retrains only when `data/data.pth` is missing or older than `src/brain/intents.json`.
- Runtime settings are saved to `data/settings.json`, which is ignored by git.
- `frontend/node_modules/` and `frontend/dist/` are generated locally and ignored by git.
- Logs are stored in the project-local `logs/` directory and ignored by git.
