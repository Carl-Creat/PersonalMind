# PersonalMind LLM Interface
import os


class LLMInterface:
    
    def __init__(self, model=None, temperature=None, max_tokens=None, api_key=None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.temperature = temperature or 0.7
        self.max_tokens = max_tokens or 2000
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.messages = []
    
    def chat(self, user_input, context=""):
        messages = []
        
        if context:
            messages.append({"role": "system", "content": 
                "You are PersonalMind, a helpful AI assistant.\n\n" + context})
        else:
            messages.append({"role": "system", "content": 
                "You are PersonalMind, a helpful AI assistant."})
        
        for msg in self.messages[-10:]:
            messages.append(msg)
        
        messages.append({"role": "user", "content": user_input})
        
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
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
            return "Error: OpenAI package not installed. Run: pip install openai"
        except Exception as e:
            return "Error: " + str(e)
    
    def clear_history(self):
        self.messages = []


_llm_instance = None


def get_llm():
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMInterface()
    return _llm_instance


def reset_llm():
    global _llm_instance
    _llm_instance = None
