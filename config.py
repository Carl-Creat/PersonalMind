"""
PersonalMind 配置
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ============== LLM 配置 ==============
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))

# ============== 向量数据库配置 ==============
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./data/chromadb")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ============== 记忆配置 ==============
MEMORY_MAX_SIZE = int(os.getenv("MEMORY_MAX_SIZE", "1000"))
MEMORY_RETRIEVE_TOP_K = int(os.getenv("MEMORY_RETRIEVE_TOP_K", "5"))
EPISODIC_MEMORY_LIMIT = int(os.getenv("EPISODIC_MEMORY_LIMIT", "100"))

# ============== 工具配置 ==============
ENABLE_WEB_SEARCH = os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
ENABLE_CALCULATOR = os.getenv("ENABLE_CALCULATOR", "true").lower() == "true"
ENABLE_CODE_EXECUTOR = os.getenv("ENABLE_CODE_EXECUTOR", "false").lower() == "true"

# ============== Web UI 配置 ==============
WEB_UI_PORT = int(os.getenv("WEB_UI_PORT", "7860"))
WEB_UI_SHARE = os.getenv("WEB_UI_SHARE", "false").lower() == "true"

# ============== 数据存储 ==============
DATA_DIR = os.getenv("DATA_DIR", "./data")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "memory.db")
CONVERSATION_LOG_PATH = os.path.join(DATA_DIR, "conversations")

# ============== 系统配置 ==============
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CHROMA_PERSIST_DIR, exist_ok=True)
os.makedirs(CONVERSATION_LOG_PATH, exist_ok=True)

# ============== 验证 ==============
if not OPENAI_API_KEY:
    print("⚠️ 警告: 未设置 OPENAI_API_KEY，请在 .env 文件或环境变量中设置")
