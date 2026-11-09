# Beyond

Beyond is an experimental, modular AI assistant with a browser-based chat interface and a local command-line assistant. The web app uses Gemini for responses; the local CLI uses an Ollama model.

## Features

- Conversational chat with a modular skill router
- Web search and summaries
- Current weather and short forecasts through WeatherAPI.com
- Local time and date, including timezone lookup for a named place
- Optional local desktop skills for applications, browsers, files, terminal commands, and image analysis
- Responsive web interface with streamed responses

Historical weather lookup is not implemented. Weather and location-based timezone lookup require a WeatherAPI.com key.

## Project layout

| Path | Purpose |
| --- | --- |
| `web/` | FastAPI app and browser interface |
| `brain/` | Conversation, planning, routing, and memory logic |
| `skills/` | User-facing assistant capabilities |
| `tools/` | Integrations used by skills |
| `models/` | Gemini and Ollama providers |
| `platforms/` | Linux, Windows, and web capability definitions |
| `config/` | Desktop application, browser, and website mappings |

## Requirements

- Python 3
- A Gemini API key for the web app
- An optional WeatherAPI.com API key for weather and city timezone lookups
- Ollama and the `qwen3:8b` model for the local CLI

## Run the web app locally

Clone the repository, create a virtual environment, and install the dependencies:

```bash
git clone https://github.com/variableknown-dev/Beyond.git
cd Beyond
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root. Keep this file private and never commit API keys:

```dotenv
GEMINI_API_KEY=replace_with_your_gemini_api_key
WEATHERAPI_KEY=replace_with_your_weatherapi_key
BEYOND_DEFAULT_TIMEZONE=Asia/Kolkata
```

`GEMINI_API_KEY` is required by the web app. `WEATHERAPI_KEY` is optional, but weather and named-city timezone lookups will not work without it. `BEYOND_DEFAULT_TIMEZONE` is optional and defaults to `Asia/Kolkata`.

Start the web server:

```bash
python -m uvicorn web.app:app --reload --host 127.0.0.1 --port 8000
```

Then open <http://127.0.0.1:8000>.

## Run the local CLI

Install and start [Ollama](https://ollama.com/), then download the configured model:

```bash
ollama pull qwen3:8b
python main.py
```

The local CLI can expose operating-system capabilities. Review the enabled skills and commands before using it on a machine with sensitive files.

## Deploy on Render

Create a Render **Web Service** connected to this repository. Use:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn web.app:app --host 0.0.0.0 --port $PORT`

Add `GEMINI_API_KEY` in the service's environment settings. Add `WEATHERAPI_KEY` to enable weather and named-city timezone lookups. Do not store keys in the repository.

## Important limitations

Beyond is an early-stage, single-user project. The web app currently keeps conversation context in process-wide memory and has no sign-in, per-user isolation, or request throttling. It is not ready for a public multi-user or commercial deployment without those safeguards and a security review. Local desktop skills can interact with the machine running Beyond.

Responses may be inaccurate. Verify important information, especially weather, news, and other time-sensitive topics, with primary sources.

## License

No license has been added yet. Making the repository public does not grant permission to reuse, modify, or distribute the code. Choose and add a license before inviting public contributions or permitting commercial reuse.
