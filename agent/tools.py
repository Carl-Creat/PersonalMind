# PersonalMind Tools
import os


class Tool:
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func


class ToolRegistry:
    
    def __init__(self):
        self.tools = {}
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        self.register(Tool("web_search", "Search the web for information", self._web_search))
        self.register(Tool("calculator", "Perform calculations", self._calculator))
        self.register(Tool("time", "Get current time", self._time))
    
    def register(self, tool):
        self.tools[tool.name] = tool
    
    def get_tool(self, name):
        return self.tools.get(name)
    
    def list_tools(self):
        return list(self.tools.keys())
    
    def _web_search(self, query):
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for i, r in enumerate(ddgs.text(query, max_results=5), 1):
                    results.append(str(i) + ". " + r.get("title", "") + "\n   " + r.get("href", "") + "\n   " + r.get("body", "")[:100])
            return "\n\n".join(results) if results else "No results found"
        except ImportError:
            return "Search not available. Run: pip install duckduckgo-search"
        except Exception as e:
            return "Search error: " + str(e)
    
    def _calculator(self, expression):
        try:
            allowed = set("0123456789+-*/.() ")
            if all(c in allowed for c in expression):
                result = eval(expression)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                return str(expression) + " = " + str(result)
            return "Invalid expression"
        except Exception as e:
            return "Calculation error: " + str(e)
    
    def _time(self):
        from datetime import datetime
        now = datetime.now()
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return now.strftime("%Y-%m-%d %H:%M:%S") + " (" + days[now.weekday()] + ")"


_tool_registry = None


def get_tools():
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry


def reset_tools():
    global _tool_registry
    _tool_registry = None
