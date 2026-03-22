"""
PersonalMind 记忆系统
"""
import os
import time
import json
import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
import hashlib

from config import DATA_DIR, SQLITE_DB_PATH, MEMORY_MAX_SIZE, MEMORY_RETRIEVE_TOP_K


@dataclass
class MemoryItem:
    """记忆单元"""
    id: int
    content: str
    memory_type: str  # 'episodic', 'semantic', 'working'
    importance: float  # 0-1, 重要性评分
    access_count: int  # 访问次数
    created_at: float
    last_accessed: float
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MemoryItem':
        return cls(**data)


class MemoryDatabase:
    """记忆数据库（SQLite）"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or SQLITE_DB_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                created_at REAL NOT NULL,
                last_accessed REAL NOT NULL,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type 
            ON memories(memory_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON memories(created_at)
        """)
        
        conn.commit()
        conn.close()
    
    def add(self, content: str, memory_type: str, 
            importance: float = 0.5, metadata: Dict = None) -> int:
        """添加记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = time.time()
        metadata_json = json.dumps(metadata or {})
        
        cursor.execute("""
            INSERT INTO memories 
            (content, memory_type, importance, access_count, created_at, last_accessed, metadata)
            VALUES (?, ?, ?, 0, ?, ?, ?)
        """, (content, memory_type, importance, now, now, metadata_json))
        
        memory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return memory_id
    
    def get(self, memory_id: int) -> Optional[MemoryItem]:
        """获取单条记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_memory(row)
        return None
    
    def update_access(self, memory_id: int):
        """更新访问记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE memories 
            SET access_count = access_count + 1, last_accessed = ?
            WHERE id = ?
        """, (time.time(), memory_id))
        
        conn.commit()
        conn.close()
    
    def search(self, query: str, memory_type: str = None, 
               limit: int = 10) -> List[MemoryItem]:
        """
        搜索记忆（简单关键词匹配）
        
        实际应用中应使用向量数据库进行语义搜索
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sql = "SELECT * FROM memories WHERE content LIKE ?"
        params = [f"%{query}%"]
        
        if memory_type:
            sql += " AND memory_type = ?"
            params.append(memory_type)
        
        sql += " ORDER BY importance DESC, access_count DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_memory(row) for row in rows]
    
    def get_recent(self, memory_type: str = None, 
                   limit: int = 10) -> List[MemoryItem]:
        """获取最近的记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if memory_type:
            cursor.execute("""
                SELECT * FROM memories 
                WHERE memory_type = ?
                ORDER BY last_accessed DESC
                LIMIT ?
            """, (memory_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM memories 
                ORDER BY last_accessed DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_memory(row) for row in rows]
    
    def get_all(self, memory_type: str = None) -> List[MemoryItem]:
        """获取所有记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if memory_type:
            cursor.execute("""
                SELECT * FROM memories 
                WHERE memory_type = ?
                ORDER BY importance DESC, created_at DESC
            """, (memory_type,))
        else:
            cursor.execute("""
                SELECT * FROM memories 
                ORDER BY importance DESC, created_at DESC
            """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_memory(row) for row in rows]
    
    def delete(self, memory_id: int):
        """删除记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        conn.commit()
        conn.close()
    
    def clear(self, memory_type: str = None):
        """清空记忆"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if memory_type:
            cursor.execute("DELETE FROM memories WHERE memory_type = ?", (memory_type,))
        else:
            cursor.execute("DELETE FROM memories")
        
        conn.commit()
        conn.close()
    
    def _row_to_memory(self, row: tuple) -> MemoryItem:
        """行转记忆对象"""
        return MemoryItem(
            id=row[0],
            content=row[1],
            memory_type=row[2],
            importance=row[3],
            access_count=row[4],
            created_at=row[5],
            last_accessed=row[6],
            metadata=json.loads(row[7])
        )


class MemorySystem:
    """
    PersonalMind 记忆系统
    
    三层记忆架构：
    1. 情景记忆 (Episodic): 具体事件、对话
    2. 语义记忆 (Semantic): 事实、知识、偏好
    3. 工作记忆 (Working): 当前任务、临时信息
    """
    
    def __init__(self):
        self.db = MemoryDatabase()
        self.working_memory: List[str] = []  # 当前会话的临时记忆
    
    def remember(self, content: str, memory_type: str = 'episodic',
                importance: float = 0.5, metadata: Dict = None) -> int:
        """
        记住新内容
        
        Args:
            content: 要记忆的内容
            memory_type: 记忆类型
            importance: 重要性 (0-1)
            metadata: 额外元数据
        
        Returns:
            记忆 ID
        """
        # 检测是否应该自动提高重要性
        if '偏好' in content or '喜欢' in content or '讨厌' in content:
            importance = max(importance, 0.7)
        
        memory_id = self.db.add(
            content=content,
            memory_type=memory_type,
            importance=importance,
            metadata=metadata or {}
        )
        
        return memory_id
    
    def recall(self, query: str = None, memory_type: str = None,
              limit: int = None) -> List[Dict]:
        """
        回忆相关内容
        
        Args:
            query: 搜索关键词
            memory_type: 记忆类型过滤
            limit: 返回数量
        
        Returns:
            记忆列表
        """
        limit = limit or MEMORY_RETRIEVE_TOP_K
        
        if query:
            memories = self.db.search(query, memory_type, limit)
        else:
            memories = self.db.get_recent(memory_type, limit)
        
        # 更新访问记录
        results = []
        for mem in memories:
            self.db.update_access(mem.id)
            results.append({
                'id': mem.id,
                'content': mem.content,
                'type': mem.memory_type,
                'importance': mem.importance,
                'created_at': datetime.fromtimestamp(mem.created_at).strftime('%Y-%m-%d %H:%M')
            })
        
        return results
    
    def get_context_for_llm(self, user_input: str = None, 
                           max_memories: int = 5) -> str:
        """
        获取供 LLM 使用的上下文
        
        检索与当前对话相关的记忆
        """
        context_parts = []
        
        # 获取最近的重要记忆
        recent = self.db.get_recent(limit=max_memories)
        
        if recent:
            context_parts.append("【关于你的记忆】")
            for mem in recent:
                context_parts.append(f"- {mem.content}")
            context_parts.append("")
        
        # 如果有用户输入，检索相关内容
        if user_input:
            related = self.db.search(user_input, limit=3)
            if related:
                context_parts.append("【可能相关的信息】")
                for mem in related:
                    context_parts.append(f"- {mem.content}")
                context_parts.append("")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def forget(self, query: str) -> int:
        """
        忘记相关内容
        
        Args:
            query: 要忘记的关键词
        
        Returns:
            删除的记忆数量
        """
        memories = self.db.search(query, limit=100)
        count = len(memories)
        
        for mem in memories:
            self.db.delete(mem.id)
        
        return count
    
    def clear_working_memory(self):
        """清空工作记忆"""
        self.working_memory = []
        self.db.clear('working')
    
    def get_all_memories(self) -> Dict[str, List[Dict]]:
        """
        获取所有记忆（按类型分类）
        
        Returns:
            {'episodic': [...], 'semantic': [...], 'working': [...]}
        """
        all_memories = self.db.get_all()
        
        categorized = {
            'episodic': [],
            'semantic': [],
            'working': []
        }
        
        for mem in all_memories:
            if mem.memory_type in categorized:
                categorized[mem.memory_type].append({
                    'id': mem.id,
                    'content': mem.content,
                    'importance': mem.importance,
                    'created_at': datetime.fromtimestamp(mem.created_at).strftime('%Y-%m-%d %H:%M')
                })
        
        return categorized
    
    def get_memory_stats(self) -> Dict:
        """获取记忆统计"""
        all_mem = self.db.get_all()
        
        stats = {
            'total': len(all_mem),
            'by_type': {},
            'high_importance': 0,
            'most_accessed': None
        }
        
        for mem in all_mem:
            t = mem.memory_type
            stats['by_type'][t] = stats['by_type'].get(t, 0) + 1
            
            if mem.importance >= 0.7:
                stats['high_importance'] += 1
        
        # 找出访问最多的
        if all_mem:
            most_accessed = max(all_mem, key=lambda m: m.access_count)
            stats['most_accessed'] = {
                'content': most_accessed.content[:50],
                'access_count': most_accessed.access_count
            }
        
        return stats


# 全局实例
_memory_system: Optional[MemorySystem] = None

def get_memory() -> MemorySystem:
    """获取记忆系统实例"""
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem()
    return _memory_system

def reset_memory():
    """重置记忆系统"""
    global _memory_system
    if _memory_system:
        _memory_system.db.clear()
    _memory_system = MemorySystem()
