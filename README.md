# PersonalMind

Your personal AI brain with memory, multi-agent collaboration, and more.

Built with Python 3.9+ | Powered by DeepSeek / OpenAI

## Features

- **Memory System** - Remembers your preferences, plans, and facts automatically
- **Multi-Agent** - Multiple AI specialists work together
- **Memory Visualization** - Interactive memory network graph
- **Voice Interface** - Text-to-speech support
- **File Understanding** - Process PDFs, images, and web pages
- **Web Search** - Real-time internet search
- **Web UI & CLI** - Two interface options

## Quick Start

### 1. Clone
```bash
git clone https://github.com/Carl-Creat/PersonalMind.git
cd PersonalMind
```

### 2. Install Dependencies
```bash
py -3 -m pip install --user -r requirements.txt
```

### 3. Configure API Key

Copy `.env.example` to `.env` and fill in your API key:

**DeepSeek (recommended, free credits):**
```env
OPENAI_API_KEY=sk-your-deepseek-api-key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

**Or OpenAI:**
```env
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo
```

Get DeepSeek key: https://platform.deepseek.com
Get OpenAI key: https://platform.openai.com/api-keys

### 4. Run

**Web UI:**
```bash
py -3 main.py
```
Open http://localhost:7860 in your browser.

**CLI Mode:**
```bash
py -3 main.py --cli
```

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help |
| `/search <keyword>` | Search the web |
| `/remember <content>` | Remember something |
| `/forget <keyword>` | Delete related memories |
| `/memory` | View all memories |
| `/clear` | Clear conversation |
| `/stats` | View usage statistics |

## Architecture

```
PersonalMind/
  main.py              # Entry point
  config.py            # Configuration
  agent/
    core.py            # Main agent logic
    memory.py          # Three-layer memory system
    llm.py             # LLM interface (DeepSeek/OpenAI)
    tools.py           # Built-in tools (search, calculator)
    web_ui.py          # Gradio web interface
    voice.py           # Voice interface
    multi_agent.py     # Multi-agent collaboration
    visualization.py   # Memory visualization
    file_understanding.py  # File & image processing
```

## Memory System

PersonalMind uses a three-layer memory architecture:

- **Episodic Memory** - Records events and conversations
- **Semantic Memory** - Stores knowledge and preferences
- **Working Memory** - Tracks current tasks and plans

The system automatically remembers important information from your conversations.

## Requirements

- Python 3.9+
- DeepSeek or OpenAI API key

## Troubleshooting

**`python` command uses Python 2:**
Use `py -3` instead of `python`.

**Permission denied during pip install:**
Add `--user` flag: `py -3 -m pip install --user -r requirements.txt`

**Gradio import error:**
```bash
py -3 -m pip install --user --force-reinstall pillow gradio
```

**Port 7860 already in use:**
```bash
py -3 main.py --port 8080
```

## License

MIT
