"""
PersonalMind 核心 Agent
"""
import os
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from agent.llm import get_llm, LLMInterface
from agent.memory import get_memory, MemorySystem
from agent.tools import get_tools, ToolRegistry


class PersonalMindAgent:
    """
    PersonalMind 核心 Agent
    
    整合 LLM、记忆系统和工具集
    """
    
    def __init__(self, user_name: str = "用户"):
        self.user_name = user_name
        self.llm = get_llm()
        self.memory = get_memory()
        self.tools = get_tools()
        
        # 对话状态
        self.is_first_session = True
        self.session_start = datetime.now()
        
        # 统计
        self.stats = {
            "total_queries": 0,
            "tools_used": {},
            "memories_stored": 0
        }
    
    def chat(self, user_input: str) -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
        
        Returns:
            AI 回复
        """
        self.stats["total_queries"] += 1
        
        # 处理命令
        if user_input.startswith("/"):
            return self._handle_command(user_input)
        
        # 检测是否应该记住某些信息
        self._auto_remember(user_input)
        
        # 获取相关记忆作为上下文
        context = self.memory.get_context_for_llm(user_input)
        
        # 决定是否使用工具
        response = self._decide_and_execute(user_input, context)
        
        return response
    
    def _handle_command(self, command: str) -> str:
        """处理命令"""
        parts = command[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "help":
            return self._show_help()
        
        elif cmd == "search":
            if not args:
                return "请提供搜索关键词，格式：/search <关键词>"
            return self._do_search(args)
        
        elif cmd == "remember":
            if not args:
                return "请提供要记住的内容，格式：/remember <内容>"
            return self._do_remember(args)
        
        elif cmd == "forget":
            if not args:
                return "请提供要忘记的关键词，格式：/forget <关键词>"
            return self._do_forget(args)
        
        elif cmd == "memory":
            return self._show_memories()
        
        elif cmd == "clear":
            self.llm.clear_history()
            return "对话历史已清空"
        
        elif cmd == "stats":
            return self._show_stats()
        
        else:
            return f"未知命令：{cmd}。输入 /help 查看可用命令。"
    
    def _decide_and_execute(self, user_input: str, context: str) -> str:
        """
        决定是否使用工具，并执行
        
        目前是简化版本，直接用 LLM 回答
        完整版本应该实现 ReAct 循环
        """
        # 检查是否需要搜索
        search_keywords = ["搜索", "查找", "最新", "今天", "现在", "新闻"]
        needs_search = any(kw in user_input for kw in search_keywords)
        
        if needs_search and "web_search" in self.tools.list_tools():
            # 执行搜索
            keyword = user_input.replace("搜索", "").replace("查找", "").strip()
            if not keyword:
                keyword = user_input
            
            search_result = self.tools.get_tool("web_search").func(keyword)
            
            # 带搜索结果的对话
            full_context = context + f"\n\n【联网搜索结果】\n{search_result}"
            response = self.llm.chat(user_input, full_context)
            
            self._track_tool_usage("web_search")
            return response
        
        # 普通对话
        return self.llm.chat(user_input, context)
    
    def _auto_remember(self, user_input: str):
        """
        自动记住重要信息
        
        检测用户提到的偏好、计划、事实等
        """
        auto_remember_keywords = [
            ("喜欢", "semantic", 0.8),
            ("讨厌", "semantic", 0.8),
            ("我是", "semantic", 0.7),
            ("我叫", "semantic", 0.8),
            ("我的", "semantic", 0.6),
            ("计划", "working", 0.7),
            ("要", "working", 0.5),
            ("会议", "episodic", 0.7),
            ("生日", "episodic", 0.9),
        ]
        
        for keyword, mem_type, importance in auto_remember_keywords:
            if keyword in user_input:
                # 检查是否已记住类似内容
                existing = self.memory.recall(keyword, limit=1)
                if not existing:
                    self.memory.remember(
                        content=user_input,
                        memory_type=mem_type,
                        importance=importance
                    )
                    self.stats["memories_stored"] += 1
    
    def _do_search(self, query: str) -> str:
        """执行搜索"""
        tool = self.tools.get_tool("web_search")
        if not tool:
            return "搜索功能暂时不可用"
        
        self._track_tool_usage("web_search")
        return tool.func(query)
    
    def _do_remember(self, content: str) -> str:
        """记住内容"""
        self.memory.remember(content, memory_type="semantic", importance=0.8)
        self.stats["memories_stored"] += 1
        return f"已记住：{content}"
    
    def _do_forget(self, keyword: str) -> str:
        """忘记内容"""
        count = self.memory.forget(keyword)
        return f"已删除 {count} 条相关记忆"
    
    def _show_memories(self) -> str:
        """显示记忆"""
        all_mem = self.memory.get_all_memories()
        
        lines = ["【你的记忆】"]
        
        for mem_type, memories in all_mem.items():
            if memories:
                type_name = {
                    "episodic": "情景记忆",
                    "semantic": "语义记忆", 
                    "working": "工作记忆"
                }.get(mem_type, mem_type)
                
                lines.append(f"\n{type_name}（{len(memories)}条）：")
                for mem in memories[:5]:  # 最多显示5条
                    lines.append(f"  • {mem['content'][:50]}...")
        
        return "\n".join(lines)
    
    def _show_help(self) -> str:
        """显示帮助"""
        return """【PersonalMind 可用命令】

/help         - 显示此帮助
/search <词>  - 联网搜索
/remember <内容> - 让 AI 记住信息
/forget <词>  - 删除相关记忆
/memory       - 查看所有记忆
/clear        - 清空对话历史
/stats        - 查看使用统计

也可以直接对话，AI 会自动记住重要信息！"""

    def _show_stats(self) -> str:
        """显示统计"""
        stats = self.stats.copy()
        stats["memory_items"] = self.memory.get_memory_stats()["total"]
        
        tool_usage = []
        for tool, count in stats["tools_used"].items():
            tool_usage.append(f"  • {tool}: {count}次")
        
        lines = ["【使用统计】"]
        lines.append(f"总对话次数：{stats['total_queries']}")
        lines.append(f"记忆条目数：{stats['memory_items']}")
        lines.append(f"自动记住：{stats['memories_stored']}条")
        
        if tool_usage:
            lines.append("\n工具使用：")
            lines.extend(tool_usage)
        
        return "\n".join(lines)
    
    def _track_tool_usage(self, tool_name: str):
        """跟踪工具使用"""
        self.stats["tools_used"][tool_name] = \
            self.stats["tools_used"].get(tool_name, 0) + 1
    
    def reset(self):
        """重置 Agent"""
        self.llm.clear_history()
        self.session_start = datetime.now()
        self.stats = {
            "total_queries": 0,
            "tools_used": {},
            "memories_stored": 0
        }
    
    def get_welcome_message(self) -> str:
        """获取欢迎消息"""
        if self.is_first_session:
            self.is_first_session = False
            return f"""你好 {self.user_name}！我是 PersonalMind，你的私人 AI 大脑 🧠

我可以帮你：
• 回答问题（联网搜索最新信息）
• 记住重要的事情
• 帮你规划任务

直接和我说话即可，我会自动记住重要信息。

输入 /help 查看所有命令。"""
        else:
            return "欢迎回来！有什么我可以帮你的？"


# 全局实例
_agent: Optional[PersonalMindAgent] = None

def get_agent(user_name: str = "用户") -> PersonalMindAgent:
    """获取 Agent 实例"""
    global _agent
    if _agent is None:
        _agent = PersonalMindAgent(user_name)
    return _agent

def reset_agent():
    """重置 Agent"""
    global _agent
    if _agent:
        _agent.reset()
    _agent = None
