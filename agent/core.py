# PersonalMind Core Agent
import os
import re
from datetime import datetime

from agent.llm import get_llm
from agent.memory import get_memory
from agent.tools import get_tools


class PersonalMindAgent:
    
    def __init__(self, user_name="User"):
        self.user_name = user_name
        self.llm = get_llm()
        self.memory = get_memory()
        self.tools = get_tools()
        self.is_first_session = True
        self.session_start = datetime.now()
        self.stats = {
            "total_queries": 0,
            "tools_used": {},
            "memories_stored": 0
        }
    
    def chat(self, user_input):
        self.stats["total_queries"] += 1
        
        if user_input.startswith("/"):
            return self._handle_command(user_input)
        
        self._auto_remember(user_input)
        context = self.memory.get_context_for_llm(user_input)
        return self._decide_and_execute(user_input, context)
    
    def _handle_command(self, command):
        parts = command[1:].split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "help":
            return self._show_help()
        elif cmd == "search":
            if not args:
                return "Usage: /search <keyword>"
            return self._do_search(args)
        elif cmd == "remember":
            if not args:
                return "Usage: /remember <content>"
            return self._do_remember(args)
        elif cmd == "forget":
            if not args:
                return "Usage: /forget <keyword>"
            return self._do_forget(args)
        elif cmd == "memory":
            return self._show_memories()
        elif cmd == "clear":
            self.llm.clear_history()
            return "Conversation history cleared"
        elif cmd == "stats":
            return self._show_stats()
        else:
            return "Unknown command. Type /help for available commands."
    
    def _decide_and_execute(self, user_input, context):
        search_keywords = ["search", "find", "latest", "news"]
        needs_search = any(kw in user_input.lower() for kw in search_keywords)
        
        if needs_search and "web_search" in self.tools.list_tools():
            keyword = user_input
            search_result = self.tools.get_tool("web_search").func(keyword)
            full_context = context + "\n\n[Web Search Results]\n" + search_result
            response = self.llm.chat(user_input, full_context)
            self._track_tool_usage("web_search")
            return response
        
        return self.llm.chat(user_input, context)
    
    def _auto_remember(self, user_input):
        keywords = [
            ("like", "semantic", 0.8),
            ("hate", "semantic", 0.8),
            ("I am", "semantic", 0.7),
            ("my", "semantic", 0.6),
            ("plan", "working", 0.7),
            ("meeting", "episodic", 0.7),
            ("birthday", "episodic", 0.9),
        ]
        
        for keyword, mem_type, importance in keywords:
            if keyword.lower() in user_input.lower():
                existing = self.memory.recall(keyword, limit=1)
                if not existing:
                    self.memory.remember(
                        content=user_input,
                        memory_type=mem_type,
                        importance=importance
                    )
                    self.stats["memories_stored"] += 1
    
    def _do_search(self, query):
        tool = self.tools.get_tool("web_search")
        if not tool:
            return "Search tool not available"
        self._track_tool_usage("web_search")
        return tool.func(query)
    
    def _do_remember(self, content):
        self.memory.remember(content, memory_type="semantic", importance=0.8)
        self.stats["memories_stored"] += 1
        return "Remembered: " + content
    
    def _do_forget(self, keyword):
        count = self.memory.forget(keyword)
        return "Deleted " + str(count) + " related memories"
    
    def _show_memories(self):
        all_mem = self.memory.get_all_memories()
        lines = ["[Your Memories]"]
        for mem_type, memories in all_mem.items():
            if memories:
                type_name = {
                    "episodic": "Episodic",
                    "semantic": "Semantic",
                    "working": "Working"
                }.get(mem_type, mem_type)
                lines.append("\n" + type_name + " (" + str(len(memories)) + "):")
                for mem in memories[:5]:
                    lines.append("  - " + mem["content"][:50])
        return "\n".join(lines)
    
    def _show_help(self):
        return """[PersonalMind Commands]

/help         - Show this help
/search <kw>  - Search the web
/remember <c> - Remember something
/forget <kw>   - Forget memories
/memory        - View all memories
/clear         - Clear conversation
/stats         - View statistics

You can also chat normally, I'll remember important things!"""
    
    def _show_stats(self):
        stats = self.stats.copy()
        stats["memory_items"] = self.memory.get_memory_stats()["total"]
        lines = ["[Statistics]"]
        lines.append("Total queries: " + str(stats["total_queries"]))
        lines.append("Memory items: " + str(stats["memory_items"]))
        lines.append("Auto-remembered: " + str(stats["memories_stored"]))
        return "\n".join(lines)
    
    def _track_tool_usage(self, tool_name):
        self.stats["tools_used"][tool_name] = \
            self.stats["tools_used"].get(tool_name, 0) + 1
    
    def reset(self):
        self.llm.clear_history()
        self.session_start = datetime.now()
        self.stats = {"total_queries": 0, "tools_used": {}, "memories_stored": 0}
    
    def get_welcome_message(self):
        if self.is_first_session:
            self.is_first_session = False
            return "Hello! I'm PersonalMind, your personal AI brain. I can help you: answer questions (with web search), remember important things, and assist with tasks. Just chat with me! Type /help for commands."
        else:
            return "Welcome back! How can I help you?"


_agent = None


def get_agent(user_name="User"):
    global _agent
    if _agent is None:
        _agent = PersonalMindAgent(user_name)
    return _agent


def reset_agent():
    global _agent
    if _agent:
        _agent.reset()
    _agent = None
