# PersonalMind Memory System - RAM Version
# This version stores memories in memory only (no disk write required)
import time
from datetime import datetime


class MemorySystem:
    """In-memory memory system - no file writes required"""
    
    def __init__(self):
        self.memories = []
        self._memory_id = 0
    
    def remember(self, content, memory_type="episodic", importance=0.5):
        self._memory_id += 1
        memory = {
            "id": self._memory_id,
            "content": content,
            "memory_type": memory_type,
            "importance": importance,
            "access_count": 0,
            "created_at": time.time(),
            "last_accessed": time.time()
        }
        self.memories.append(memory)
        return self._memory_id
    
    def recall(self, query=None, memory_type=None, limit=5):
        results = []
        for mem in reversed(self.memories):
            if memory_type and mem["memory_type"] != memory_type:
                continue
            if query:
                if query.lower() in mem["content"].lower():
                    mem["access_count"] += 1
                    mem["last_accessed"] = time.time()
                    results.append({
                        "id": mem["id"],
                        "content": mem["content"],
                        "type": mem["memory_type"],
                        "importance": mem["importance"],
                        "created_at": datetime.fromtimestamp(mem["created_at"]).strftime("%Y-%m-%d %H:%M")
                    })
                    if len(results) >= limit:
                        break
            else:
                mem["access_count"] += 1
                mem["last_accessed"] = time.time()
                results.append({
                    "id": mem["id"],
                    "content": mem["content"],
                    "type": mem["memory_type"],
                    "importance": mem["importance"],
                    "created_at": datetime.fromtimestamp(mem["created_at"]).strftime("%Y-%m-%d %H:%M")
                })
                if len(results) >= limit:
                    break
        return results
    
    def get_context_for_llm(self, user_input=None, max_memories=5):
        parts = []
        recent = self.memories[-max_memories:] if self.memories else []
        if recent:
            parts.append("[Your Memories]")
            for mem in recent[-3:]:
                parts.append("- " + mem["content"][:100])
        return "\n".join(parts) if parts else ""
    
    def forget(self, query):
        original_count = len(self.memories)
        self.memories = [m for m in self.memories if query.lower() not in m["content"].lower()]
        return original_count - len(self.memories)
    
    def get_all_memories(self):
        categorized = {"episodic": [], "semantic": [], "working": []}
        for mem in self.memories:
            if mem["memory_type"] in categorized:
                categorized[mem["memory_type"]].append({
                    "id": mem["id"],
                    "content": mem["content"],
                    "importance": mem["importance"],
                    "created_at": datetime.fromtimestamp(mem["created_at"]).strftime("%Y-%m-%d %H:%M")
                })
        return categorized
    
    def get_memory_stats(self):
        by_type = {"episodic": 0, "semantic": 0, "working": 0}
        high_imp = 0
        for mem in self.memories:
            if mem["memory_type"] in by_type:
                by_type[mem["memory_type"]] += 1
            if mem["importance"] >= 0.7:
                high_imp += 1
        return {
            "total": len(self.memories),
            "by_type": by_type,
            "high_importance": high_imp
        }
    
    def clear(self, memory_type=None):
        if memory_type:
            self.memories = [m for m in self.memories if m["memory_type"] != memory_type]
        else:
            self.memories = []


_memory_system = None


def get_memory():
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem()
    return _memory_system


def reset_memory():
    global _memory_system
    _memory_system = None
