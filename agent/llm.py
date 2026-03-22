"""
PersonalMind LLM 接口
"""
import os
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS


class LLMInterface:
    """
    LLM 接口封装
    
    支持 OpenAI API 及兼容 API
    """
    
    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        api_key: str = None
    ):
        self.model = model or OPENAI_MODEL
        self.temperature = temperature or OPENAI_TEMPERATURE
        self.max_tokens = max_tokens or OPENAI_MAX_TOKENS
        self.api_key = api_key or OPENAI_API_KEY
        
        # 初始化 ChatOpenAI
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            api_key=self.api_key
        )
        
        # 对话历史
        self.messages: List[Dict] = []
        
        # 系统提示词
        self.system_prompt = self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示词"""
        return """你是一个智能个人助手，名叫 PersonalMind。

你的特点是：
1. 聪明、有耐心、乐于助人
2. 能够记住用户的偏好和重要信息
3. 回答问题准确、简洁、有条理
4. 在适当时候提供建议

用户希望你记住的信息请特别关注。
如果你需要搜索信息来回答问题，可以使用搜索工具。
"""
    
    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        self.system_prompt = prompt
    
    def add_user_message(self, content: str):
        """添加用户消息"""
        self.messages.append({"role": "user", "content": content})
    
    def add_ai_message(self, content: str):
        """添加 AI 消息"""
        self.messages.append({"role": "assistant", "content": content})
    
    def clear_history(self):
        """清空对话历史"""
        self.messages = []
    
    def chat(self, user_input: str, context: str = "") -> str:
        """
        对话
        
        Args:
            user_input: 用户输入
            context: 额外上下文（记忆检索结果等）
        
        Returns:
            AI 回复
        """
        # 构建消息列表
        messages = [
            SystemMessage(content=self.system_prompt)
        ]
        
        # 添加上下文（如果有）
        if context:
            context_msg = f"\n\n[用户相关记忆/上下文]\n{context}"
            messages.append(SystemMessage(content=context_msg))
        
        # 添加历史对话（保留最近几轮）
        recent_messages = self.messages[-10:]  # 最近10条
        for msg in recent_messages:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        
        # 添加当前输入
        messages.append(HumanMessage(content=user_input))
        
        try:
            # 调用 LLM
            response = self.llm.invoke(messages)
            reply = response.content
            
            # 保存对话历史
            self.add_user_message(user_input)
            self.add_ai_message(reply)
            
            return reply
            
        except Exception as e:
            return f"抱歉，发生了错误：{str(e)}"
    
    def chat_with_tools(
        self, 
        user_input: str, 
        tools: List[callable],
        context: str = ""
    ) -> str:
        """
        使用工具的对话
        
        Args:
            user_input: 用户输入
            tools: 可用工具列表
            context: 额外上下文
        
        Returns:
            AI 回复
        """
        # 简单的 ReAct 实现
        # 1. LLM 判断是否需要使用工具
        # 2. 执行工具
        # 3. LLM 根据结果生成回复
        
        # 构建提示
        tool_desc = "\n".join([f"- {t.__name__}: {t.__doc__ or '无描述'}" for t in tools])
        
        prompt = f"""
你是一个智能助手。以下是你可用的工具：
{tool_desc}

用户问题: {user_input}

{context}

请决定是否需要使用工具来回答问题。
如果需要，请用以下格式回复：
[TOOL_CALL] 工具名 | 参数
如果不需要，直接回答。
"""
        
        # 简单实现：直接回答
        return self.chat(user_input, context)
    
    def get_conversation_summary(self) -> str:
        """获取对话摘要"""
        if not self.messages:
            return "暂无对话记录"
        
        summary = f"对话记录（共 {len(self.messages)} 条消息）：\n"
        for i, msg in enumerate(self.messages[-6:], 1):
            role = "用户" if msg["role"] == "user" else "AI"
            content = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
            summary += f"{i}. {role}: {content}\n"
        
        return summary


# 全局实例
_llm_instance: Optional[LLMInterface] = None

def get_llm() -> LLMInterface:
    """获取 LLM 实例"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMInterface()
    return _llm_instance

def reset_llm():
    """重置 LLM 实例"""
    global _llm_instance
    _llm_instance = None
