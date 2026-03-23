"""
持久化记忆存储 (SQLite)

将三层记忆系统持久化到本地 SQLite 数据库，
解决重启后记忆丢失的问题。

特性:
- 自动创建数据库和表结构
- 支持增删改查
- 支持关键词搜索
- 支持按类型过滤 (episodic/semantic/working)
- 自动清理过期的 working memory
"""

import sqlite3
import json
import time
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'memory.db')


def get_db_path() -> str:
    """获取数据库路径，支持环境变量覆盖"""
    return os.environ.get('MEMORY_DB_PATH', DB_PATH)


class MemoryStore:
    """
    SQLite 持久化记忆存储
    
    表结构:
        memories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            type        TEXT NOT NULL,          -- episodic/semantic/working
            content     TEXT NOT NULL,          -- 记忆内容
            metadata    TEXT DEFAULT '{}',      -- JSON 元数据
            importance  REAL DEFAULT 0.5,       -- 重要性评分 0-1
            created_at  REAL NOT NULL,          -- 创建时间戳
            accessed_at REAL NOT NULL,          -- 最后访问时间戳
            access_count INTEGER DEFAULT 0      -- 访问次数
        )
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_db_path()
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """初始化数据库表结构"""
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    type        TEXT NOT NULL,
                    content     TEXT NOT NULL,
                    metadata    TEXT DEFAULT '{}',
                    importance  REAL DEFAULT 0.5,
                    created_at  REAL NOT NULL,
                    accessed_at REAL NOT NULL,
                    access_count INTEGER DEFAULT 0
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON memories(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memories(importance DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON memories(created_at DESC)")
            conn.commit()

    def add(
        self,
        content: str,
        memory_type: str = "episodic",
        metadata: Optional[Dict] = None,
        importance: float = 0.5
    ) -> int:
        """
        添加一条记忆
        
        Args:
            content: 记忆内容
            memory_type: 类型 (episodic/semantic/working)
            metadata: 额外元数据
            importance: 重要性 0-1
        
        Returns:
            新记忆的 ID
        """
        now = time.time()
        with self._get_conn() as conn:
            cursor = conn.execute(
                """INSERT INTO memories (type, content, metadata, importance, created_at, accessed_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (memory_type, content, json.dumps(metadata or {}), importance, now, now)
            )
            conn.commit()
            return cursor.lastrowid

    def get(self, memory_id: int) -> Optional[Dict]:
        """根据 ID 获取记忆"""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM memories WHERE id = ?", (memory_id,)).fetchone()
            if row:
                self._update_access(conn, memory_id)
                return self._row_to_dict(row)
        return None

    def search(
        self,
        keyword: str,
        memory_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        关键词搜索记忆
        
        Args:
            keyword: 搜索关键词
            memory_type: 过滤类型 (None 表示全部)
            limit: 最大返回数量
        
        Returns:
            匹配的记忆列表，按重要性排序
        """
        query = "SELECT * FROM memories WHERE content LIKE ?"
        params: List = [f"%{keyword}%"]
        if memory_type:
            query += " AND type = ?"
            params.append(memory_type)
        query += " ORDER BY importance DESC, accessed_at DESC LIMIT ?"
        params.append(limit)

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def get_all(
        self,
        memory_type: Optional[str] = None,
        limit: int = 50,
        min_importance: float = 0.0
    ) -> List[Dict]:
        """获取所有记忆，按重要性排序"""
        query = "SELECT * FROM memories WHERE importance >= ?"
        params: List = [min_importance]
        if memory_type:
            query += " AND type = ?"
            params.append(memory_type)
        query += " ORDER BY importance DESC, accessed_at DESC LIMIT ?"
        params.append(limit)

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def delete(self, memory_id: int) -> bool:
        """删除指定记忆"""
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            conn.commit()
            return cursor.rowcount > 0

    def delete_by_keyword(self, keyword: str) -> int:
        """删除包含关键词的记忆，返回删除数量"""
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE content LIKE ?", (f"%{keyword}%",))
            conn.commit()
            return cursor.rowcount

    def update_importance(self, memory_id: int, importance: float):
        """更新记忆重要性"""
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE memories SET importance = ? WHERE id = ?",
                (max(0.0, min(1.0, importance)), memory_id)
            )
            conn.commit()

    def cleanup_working_memory(self, max_age_hours: float = 24.0):
        """清理过期的 working memory"""
        cutoff = time.time() - max_age_hours * 3600
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM memories WHERE type = 'working' AND created_at < ?",
                (cutoff,)
            )
            conn.commit()
            deleted = cursor.rowcount
            if deleted > 0:
                print(f"Cleaned up {deleted} expired working memories")
            return deleted

    def stats(self) -> Dict:
        """获取记忆统计信息"""
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            by_type = conn.execute(
                "SELECT type, COUNT(*) as cnt FROM memories GROUP BY type"
            ).fetchall()
            return {
                "total": total,
                "by_type": {row["type"]: row["cnt"] for row in by_type},
                "db_path": self.db_path,
                "db_size_kb": round(os.path.getsize(self.db_path) / 1024, 1) if os.path.exists(self.db_path) else 0
            }

    def _update_access(self, conn: sqlite3.Connection, memory_id: int):
        conn.execute(
            "UPDATE memories SET accessed_at = ?, access_count = access_count + 1 WHERE id = ?",
            (time.time(), memory_id)
        )
        conn.commit()

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict:
        d = dict(row)
        d['metadata'] = json.loads(d.get('metadata', '{}'))
        d['created_at_str'] = datetime.fromtimestamp(d['created_at']).strftime('%Y-%m-%d %H:%M:%S')
        return d


# ==================== 便捷函数 ====================

_store: Optional[MemoryStore] = None

def get_store() -> MemoryStore:
    """获取全局 MemoryStore 单例"""
    global _store
    if _store is None:
        _store = MemoryStore()
    return _store

def remember(content: str, memory_type: str = "episodic", importance: float = 0.5) -> int:
    """快捷记忆函数"""
    return get_store().add(content, memory_type, importance=importance)

def recall(keyword: str, limit: int = 5) -> List[Dict]:
    """快捷回忆函数"""
    return get_store().search(keyword, limit=limit)

def forget(keyword: str) -> int:
    """快捷遗忘函数"""
    return get_store().delete_by_keyword(keyword)
