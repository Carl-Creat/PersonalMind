# PersonalMind Configuration
import os

# Load .env file manually (no dotenv dependency)
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, _, value = line.partition('=')
                os.environ.setdefault(key.strip(), value.strip())

# LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "deepseek-chat")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

# Memory
MEMORY_MAX_SIZE = int(os.getenv("MEMORY_MAX_SIZE", "1000"))

# Web UI
WEB_UI_PORT = int(os.getenv("WEB_UI_PORT", "7860"))
WEB_UI_SHARE = os.getenv("WEB_UI_SHARE", "false").lower() == "true"

# Warning
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set. Please edit .env file.")
