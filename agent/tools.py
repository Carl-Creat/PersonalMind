"""
PersonalMind 工具集
"""
import os
import re
import json
import time
from typing import List, Dict, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup

from config import ENABLE_WEB_SEARCH, ENABLE_CALCULATOR


@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    func: Callable
    parameters: Dict[str, str] = None  # 参数名 -> 描述
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class ToolRegistry:
    """工具注册器"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """注册内置工具"""
        # Web Search
        if ENABLE_WEB_SEARCH:
            self.register(WebSearchTool())
        
        # Calculator
        if ENABLE_CALCULATOR:
            self.register(CalculatorTool())
        
        # Time
        self.register(TimeTool())
        
        # Note
        self.register(NoteTool())
    
    def register(self, tool: Tool):
        """注册工具"""
        self.tools[tool.name] = tool
    
    def unregister(self, name: str):
        """注销工具"""
        if name in self.tools:
            del self.tools[name]
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """列出所有工具"""
        return list(self.tools.keys())
    
    def get_tools_prompt(self) -> str:
        """获取工具描述（用于 LLM 提示）"""
        lines = ["你可用的工具："]
        for name, tool in self.tools.items():
            params = ", ".join([f"{k}: {v}" for k, v in tool.parameters.items()])
            lines.append(f"\n【{tool.name}】{tool.description}")
            if params:
                lines.append(f"  参数: {params}")
        return "\n".join(lines)


class WebSearchTool(Tool):
    """联网搜索工具"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="搜索互联网获取最新信息。当用户询问实时信息、新闻、天气预报等需要最新数据的内容时使用。",
            func=self.search,
            parameters={"query": "搜索关键词"}
        )
    
    def search(self, query: str) -> str:
        """
        搜索互联网
        
        Args:
            query: 搜索关键词
        
        Returns:
            搜索结果
        """
        try:
            # 使用 DuckDuckGo API（免费，无需 API Key）
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS() as ddgs:
                for i, r in enumerate(ddgs.text(query, max_results=5), 1):
                    results.append(
                        f"{i}. {r['title']}\n"
                        f"   {r['href']}\n"
                        f"   {r['body'][:200]}..."
                    )
            
            if not results:
                return "没有找到相关结果。"
            
            return "【搜索结果】\n\n" + "\n\n".join(results)
            
        except ImportError:
            # 备选方案：使用 requests
            return self._fallback_search(query)
        except Exception as e:
            return f"搜索失败：{str(e)}"
    
    def _fallback_search(self, query: str) -> str:
        """备选搜索方案"""
        try:
            # 使用 Wikipedia API
            url = f"https://en.wikipedia.org/w/api.php"
            params = {
                "action": "opensearch",
                "search": query,
                "limit": 5,
                "format": "json"
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            
            if len(data) >= 4 and data[1]:
                results = [f"{i+1}. {title}" for i, title in enumerate(data[1])]
                return "【相关条目】\n" + "\n".join(results)
            
            return "没有找到相关结果。"
        except:
            return "搜索服务暂时不可用。"


class CalculatorTool(Tool):
    """计算器工具"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算。支持加减乘除、幂运算、括号等基本运算。",
            func=self.calculate,
            parameters={"expression": "数学表达式，如 2+3*4"}
        )
    
    def calculate(self, expression: str) -> str:
        """
        执行计算
        
        Args:
            expression: 数学表达式
        
        Returns:
            计算结果
        """
        try:
            # 安全检查：只允许数字和运算符
            allowed = set("0123456789+-*/.() ")
            if not all(c in allowed for c in expression):
                return "表达式包含不支持的字符"
            
            # 评估表达式
            result = eval(expression)
            
            # 格式化结果
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 10)
            
            return f"计算结果：{expression} = {result}"
            
        except ZeroDivisionError:
            return "错误：除数不能为零"
        except Exception as e:
            return f"计算错误：{str(e)}"


class TimeTool(Tool):
    """时间工具"""
    
    def __init__(self):
        super().__init__(
            name="time",
            description="获取当前时间和日期。无需参数。",
            func=self.get_time,
            parameters={}
        )
    
    def get_time(self, *args) -> str:
        """
        获取当前时间
        
        Returns:
            当前时间
        """
        now = datetime.now()
        return (
            f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}\n"
            f"星期{['一','二','三','四','五','六','日'][now.weekday()]}"
        )


class NoteTool(Tool):
    """笔记工具"""
    
    def __init__(self):
        super().__init__(
            name="note",
            description="创建或查看笔记。可以保存重要信息供以后查看。",
            func=self.manage_note,
            parameters={
                "action": "操作：'save' 保存 或 'list' 查看",
                "content": "笔记内容（save时需要）"
            }
        )
        self.notes_file = os.path.join(
            os.path.dirname(__file__), 
            "..", "data", "notes.json"
        )
        os.makedirs(os.path.dirname(self.notes_file), exist_ok=True)
        self.notes = self._load_notes()
    
    def _load_notes(self) -> List[Dict]:
        """加载笔记"""
        if os.path.exists(self.notes_file):
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_notes(self):
        """保存笔记"""
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=2)
    
    def manage_note(self, action: str = "list", content: str = "") -> str:
        """
        管理笔记
        
        Args:
            action: 操作类型
            content: 笔记内容
        
        Returns:
            操作结果
        """
        if action.lower() == "save":
            if not content:
                return "请提供要保存的内容"
            
            self.notes.append({
                "content": content,
                "created_at": datetime.now().strftime('%Y-%m-%d %H:%M'),
                "id": len(self.notes) + 1
            })
            self._save_notes()
            return f"已保存笔记（共 {len(self.notes)} 条）"
        
        elif action.lower() == "list":
            if not self.notes:
                return "暂无笔记"
            
            lines = [f"【笔记列表】（共 {len(self.notes)} 条）"]
            for note in self.notes[-10:]:  # 最近10条
                lines.append(f"\n{note['id']}. {note['content']}")
                lines.append(f"   创建于：{note['created_at']}")
            
            return "\n".join(lines)
        
        else:
            return "未知操作，请使用 'save' 或 'list'"


class CodeExecutorTool(Tool):
    """代码执行工具"""
    
    def __init__(self):
        super().__init__(
            name="execute_code",
            description="执行 Python 代码。注意：可能存在安全风险，请谨慎使用。",
            func=self.execute,
            parameters={"code": "Python 代码"}
        )
    
    def execute(self, code: str) -> str:
        """
        执行代码
        
        Args:
            code: Python 代码
        
        Returns:
            执行结果
        """
        try:
            # 安全检查
            dangerous = ["import os", "import sys", "import subprocess", 
                        "__import__", "eval(", "exec(", "open(",
                        "requests", "urllib", "socket"]
            
            for pattern in dangerous:
                if pattern in code:
                    return f"安全检查：代码包含禁止的模式 '{pattern}'"
            
            # 捕获输出
            import io
            from contextlib import redirect_stdout
            
            output = io.StringIO()
            exec_globals = {"__name__": "__main__"}
            
            with redirect_stdout(output):
                exec(code, exec_globals)
            
            result = output.getvalue()
            
            if not result:
                return "代码执行完成，无输出"
            
            return f"【执行结果】\n{result}"
            
        except Exception as e:
            return f"执行错误：{str(e)}"


# 全局工具注册器
_tool_registry: Optional[ToolRegistry] = None

def get_tools() -> ToolRegistry:
    """获取工具注册器"""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry

def reset_tools():
    """重置工具注册器"""
    global _tool_registry
    _tool_registry = None
