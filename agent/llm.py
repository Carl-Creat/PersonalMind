# PersonalMind LLM Interface - Multi-Provider Support
import os


# Supported providers with default settings
PROVIDERS = {
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "default_model": "deepseek-chat",
        "api_key_env": "DEEPSEEK_API_KEY",
        "website": "https://platform.deepseek.com",
    },
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "default_model": "gpt-4o-mini",
        "api_key_env": "OPENAI_API_KEY",
        "website": "https://platform.openai.com/api-keys",
    },
    "qwen": {
        "name": "Qwen (Alibaba)",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen-turbo", "qwen-plus", "qwen-max"],
        "default_model": "qwen-turbo",
        "api_key_env": "QWEN_API_KEY",
        "website": "https://dashscope.console.aliyun.com/",
    },
    "kimi": {
        "name": "Kimi (Moonshot)",
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
        "default_model": "moonshot-v1-8k",
        "api_key_env": "KIMI_API_KEY",
        "website": "https://platform.moonshot.cn/",
    },
    "zhipu": {
        "name": "Zhipu AI (GLM)",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": ["glm-4-flash", "glm-4-air", "glm-4-plus", "glm-4"],
        "default_model": "glm-4-flash",
        "api_key_env": "ZHIPU_API_KEY",
        "website": "https://open.bigmodel.cn/",
    },
    "doubao": {
        "name": "Doubao (ByteDance)",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "models": ["doubao-pro-4k", "doubao-pro-32k", "doubao-pro-128k"],
        "default_model": "doubao-pro-4k",
        "api_key_env": "DOUBAO_API_KEY",
        "website": "https://console.volcengine.com/ark",
    },
    "ernie": {
        "name": "ERNIE (Baidu)",
        "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat",
        "models": ["ernie-bot-turbo", "ernie-bot", "ernie-bot-4"],
        "default_model": "ernie-bot-turbo",
        "api_key_env": "ERNIE_API_KEY",
        "website": "https://cloud.baidu.com/product/wenxinworkshop",
    },
    "claude": {
        "name": "Claude (Anthropic)",
        "base_url": "https://api.anthropic.com",
        "models": ["claude-3-haiku-20240307", "claude-3-sonnet-20240229", "claude-3-opus-20240229", "claude-3-5-sonnet-20241022"],
        "default_model": "claude-3-haiku-20240307",
        "api_key_env": "CLAUDE_API_KEY",
        "website": "https://console.anthropic.com/",
    },
    "gemini": {
        "name": "Gemini (Google)",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        "default_model": "gemini-2.0-flash",
        "api_key_env": "GEMINI_API_KEY",
        "website": "https://aistudio.google.com/apikey",
    },
    "mistral": {
        "name": "Mistral",
        "base_url": "https://api.mistral.ai/v1",
        "models": ["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest", "codestral-latest"],
        "default_model": "mistral-small-latest",
        "api_key_env": "MISTRAL_API_KEY",
        "website": "https://console.mistral.ai/",
    },
    "siliconflow": {
        "name": "SiliconFlow",
        "base_url": "https://api.siliconflow.cn/v1",
        "models": ["deepseek-ai/DeepSeek-V3", "Qwen/Qwen2.5-72B-Instruct", "THUDM/glm-4-9b-chat"],
        "default_model": "deepseek-ai/DeepSeek-V3",
        "api_key_env": "SILICONFLOW_API_KEY",
        "website": "https://cloud.siliconflow.cn/",
    },
    "custom": {
        "name": "Custom (OpenAI compatible)",
        "base_url": "",
        "models": [],
        "default_model": "",
        "api_key_env": "CUSTOM_API_KEY",
        "website": "",
    },
}


class LLMInterface:
    
    def __init__(self, provider=None, model=None, temperature=None, max_tokens=None, api_key=None, base_url=None):
        self.provider_key = provider or os.getenv("AI_PROVIDER", "deepseek")
        self.model = model
        self.temperature = temperature or 0.7
        self.max_tokens = max_tokens or 2000
        self.base_url = base_url
        self.api_key = api_key
        self.messages = []
        
        # Resolve provider settings
        self._resolve_provider()
    
    def _resolve_provider(self):
        provider = PROVIDERS.get(self.provider_key)
        
        if provider:
            # API key priority: constructor > env var > OPENAI_API_KEY fallback
            if not self.api_key:
                self.api_key = os.getenv(provider["api_key_env"], "") or os.getenv("OPENAI_API_KEY", "")
            if not self.base_url:
                self.base_url = provider["base_url"]
            if not self.model:
                self.model = os.getenv("AI_MODEL", provider["default_model"])
        else:
            # Custom provider
            if not self.api_key:
                self.api_key = os.getenv("CUSTOM_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
            if not self.base_url:
                self.base_url = os.getenv("OPENAI_BASE_URL", "")
            if not self.model:
                self.model = os.getenv("AI_MODEL", "gpt-3.5-turbo")
    
    def chat(self, user_input, context=""):
        messages = []
        
        system_prompt = "You are PersonalMind, a helpful AI assistant."
        if context:
            system_prompt += "\n\n" + context
        messages.append({"role": "system", "content": system_prompt})
        
        for msg in self.messages[-10:]:
            messages.append(msg)
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            import openai
            kwargs = {"api_key": self.api_key}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            client = openai.OpenAI(**kwargs)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            reply = response.choices[0].message.content
            self.messages.append({"role": "user", "content": user_input})
            self.messages.append({"role": "assistant", "content": reply})
            return reply
        except ImportError:
            return "Error: openai package not installed. Run: pip install openai"
        except Exception as e:
            return "Error: " + str(e)
    
    def clear_history(self):
        self.messages = []
    
    def switch_provider(self, provider_key, api_key=None, model=None, base_url=None):
        self.provider_key = provider_key
        self.messages = []
        if api_key:
            self.api_key = api_key
        if base_url:
            self.base_url = base_url
        if model:
            self.model = model
        else:
            self.model = None
        self._resolve_provider()
        return True
    
    def get_current_info(self):
        provider = PROVIDERS.get(self.provider_key, {})
        return {
            "provider": self.provider_key,
            "provider_name": provider.get("name", "Custom"),
            "model": self.model,
            "base_url": self.base_url,
            "has_key": bool(self.api_key),
        }


_llm_instance = None


def get_llm():
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMInterface()
    return _llm_instance


def reset_llm():
    global _llm_instance
    _llm_instance = None
