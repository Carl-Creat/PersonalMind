# PersonalMind

Your personal AI brain with memory, multi-provider support, and more.

## Supported AI Providers (11+)

### China
| Provider | Models | Get API Key |
|----------|--------|-------------|
| DeepSeek | deepseek-chat, deepseek-reasoner | https://platform.deepseek.com |
| Qwen (Alibaba) | qwen-turbo, qwen-plus, qwen-max | https://dashscope.console.aliyun.com |
| Kimi (Moonshot) | moonshot-v1-8k/32k/128k | https://platform.moonshot.cn |
| Zhipu AI (GLM) | glm-4-flash/air/plus | https://open.bigmodel.cn |
| Doubao (ByteDance) | doubao-pro-4k/32k/128k | https://console.volcengine.com/ark |
| ERNIE (Baidu) | ernie-bot-turbo/4 | https://cloud.baidu.com |
| SiliconFlow | DeepSeek-V3, Qwen2.5, GLM-4 | https://cloud.siliconflow.cn |

### International
| Provider | Models | Get API Key |
|----------|--------|-------------|
| OpenAI | gpt-4o, gpt-4o-mini, gpt-3.5-turbo | https://platform.openai.com/api-keys |
| Claude (Anthropic) | claude-3-haiku/sonnet/opus | https://console.anthropic.com |
| Gemini (Google) | gemini-2.0-flash, gemini-1.5-pro | https://aistudio.google.com/apikey |
| Mistral | mistral-small/medium/large | https://console.mistral.ai |

Switch providers in the Web UI - no code changes needed.

## Features

- **11 AI Providers** - Switch between providers in the UI
- **Memory System** - Three-layer architecture (episodic, semantic, working)
- **Multi-Agent** - Multiple AI specialists collaborate
- **Memory Visualization** - Interactive memory network graph
- **Voice Interface** - Text-to-speech support
- **File Understanding** - Process PDFs, images, web pages
- **Web Search** - Real-time internet search
- **Calculator** - Built-in math tool
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

### 3. Configure

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` - set your provider and API key:
```env
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-your-key-here
```

Or set it directly in the Web UI (no .env needed).

### 4. Run

**Web UI (recommended):**
```bash
py -3 main.py
```
Open http://localhost:7860 - select provider and enter API key on the right panel.

**CLI Mode:**
```bash
py -3 main.py --cli
```

## Commands (CLI)

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
  .env.example         # Config template
  agent/
    core.py            # Main agent logic
    llm.py             # Multi-provider LLM interface
    memory.py          # Three-layer memory system
    tools.py           # Built-in tools
    web_ui.py          # Gradio web interface
    voice.py           # Voice interface
    multi_agent.py     # Multi-agent collaboration
    visualization.py   # Memory visualization
    file_understanding.py  # File processing
```

## Configuration Reference

```env
# Provider: deepseek, openai, qwen, kimi, zhipu, doubao, ernie, claude, gemini, mistral, siliconflow, custom
AI_PROVIDER=deepseek

# API Keys (set the one for your provider)
DEEPSEEK_API_KEY=
OPENAI_API_KEY=
QWEN_API_KEY=
KIMI_API_KEY=
ZHIPU_API_KEY=
DOUBAO_API_KEY=
ERNIE_API_KEY=
CLAUDE_API_KEY=
GEMINI_API_KEY=
MISTRAL_API_KEY=
SILICONFLOW_API_KEY=
CUSTOM_API_KEY=

# Custom provider URL (when AI_PROVIDER=custom)
OPENAI_BASE_URL=

# Override default model (optional)
# AI_MODEL=

# Web UI
WEB_UI_PORT=7860
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `python` uses Python 2 | Use `py -3` instead |
| Permission denied | Add `--user`: `py -3 -m pip install --user -r requirements.txt` |
| Gradio import error | `py -3 -m pip install --user --force-reinstall pillow gradio` |
| Port 7860 in use | `py -3 main.py --port 8080` |
| GBK encoding error | Make sure `.env` has no Chinese characters |

## License

MIT
