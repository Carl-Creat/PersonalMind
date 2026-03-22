# PersonalMind Configuration
import os

# Load .env file manually
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                os.environ.setdefault(key.strip(), value.strip())

# ============== AI Provider ==============
# Options: deepseek, openai, qwen, kimi, zhipu, doubao, ernie, claude, gemini, mistral, siliconflow, custom
AI_PROVIDER = os.getenv("AI_PROVIDER", "deepseek")
AI_MODEL = os.getenv("AI_MODEL", "")

# API Keys (set your provider's key here, or use the provider-specific env var)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "")
KIMI_API_KEY = os.getenv("KIMI_API_KEY", "")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
ERNIE_API_KEY = os.getenv("ERNIE_API_KEY", "")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
CUSTOM_API_KEY = os.getenv("CUSTOM_API_KEY", "")

# Custom provider settings (when AI_PROVIDER=custom)
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")

# ============== LLM Settings ==============
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

# ============== Memory ==============
MEMORY_MAX_SIZE = int(os.getenv("MEMORY_MAX_SIZE", "1000"))

# ============== Web UI ==============
WEB_UI_PORT = int(os.getenv("WEB_UI_PORT", "7860"))
WEB_UI_SHARE = os.getenv("WEB_UI_SHARE", "false").lower() == "true"
