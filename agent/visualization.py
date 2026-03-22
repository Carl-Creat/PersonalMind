"""
PersonalMind 记忆可视化模块

生成漂亮的记忆网络图，展示 AI 如何理解和记忆用户
"""
import json
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from html import escape

from agent.memory import get_memory


@dataclass
class MemoryNode:
    """记忆节点"""
    id: str
    content: str
    node_type: str  # 'user', 'episodic', 'semantic', 'working'
    importance: float
    connections: List[str]  # 关联的节点 ID
    created_at: str


class MemoryVisualizer:
    """
    记忆可视化器
    
    生成交互式记忆网络图
    """
    
    def __init__(self):
        self.nodes: List[MemoryNode] = []
        self.center_node_id = "user"
        self._init_user_node()
    
    def _init_user_node(self):
        """初始化用户节点（中心）"""
        self.nodes.append(MemoryNode(
            id="user",
            content="你",
            node_type="user",
            importance=1.0,
            connections=[],
            created_at=datetime.now().strftime('%Y-%m-%d')
        ))
    
    def add_memory(self, content: str, memory_type: str, importance: float = 0.5):
        """添加记忆节点"""
        # 生成唯一 ID
        node_id = f"mem_{len(self.nodes)}"
        
        # 提取关键词作为连接
        connections = self._extract_connections(content)
        
        node = MemoryNode(
            id=node_id,
            content=content[:100],  # 截断显示
            node_type=memory_type,
            importance=importance,
            connections=connections,
            created_at=datetime.now().strftime('%Y-%m-%d')
        )
        
        self.nodes.append(node)
        
        # 更新用户节点的连接
        for n in self.nodes:
            if n.id == "user" and node_id not in n.connections:
                n.connections.append(node_id)
        
        return node_id
    
    def _extract_connections(self, content: str) -> List[str]:
        """从内容中提取关联"""
        connections = []
        
        # 关键词匹配
        keywords = {
            "工作": ["项目", "会议", "任务", "报告"],
            "生活": ["吃饭", "休息", "运动", "健康"],
            "学习": ["课程", "书籍", "论文", "练习"],
            "兴趣": ["喜欢", "爱好", "音乐", "电影"],
        }
        
        content_lower = content.lower()
        for category, words in keywords.items():
            for word in words:
                if word in content_lower:
                    conn_id = f"concept_{category}"
                    if conn_id not in connections:
                        connections.append(conn_id)
        
        return connections
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        by_type = {"episodic": 0, "semantic": 0, "working": 0}
        total_importance = 0
        high_importance_count = 0
        
        for node in self.nodes:
            if node.node_type in by_type:
                by_type[node.node_type] += 1
            total_importance += node.importance
            if node.importance >= 0.7:
                high_importance_count += 1
        
        # 计算理解度（基于记忆数量和重要性）
        understanding = min(100, len(self.nodes) * 5 + high_importance_count * 10)
        
        return {
            "total_memories": len(self.nodes) - 1,  # 减去用户节点
            "by_type": by_type,
            "understanding": understanding,
            "high_importance": high_importance_count
        }
    
    def generate_html(self) -> str:
        """生成交互式 HTML"""
        stats = self.get_stats()
        
        # 构建节点 JSON
        nodes_json = []
        for node in self.nodes:
            nodes_json.append({
                "id": node.id,
                "label": node.content[:20] + ("..." if len(node.content) > 20 else ""),
                "full_content": node.content,
                "type": node.node_type,
                "importance": node.importance,
                "connections": node.connections,
                "created": node.created_at
            })
        
        nodes_str = json.dumps(nodes_json, ensure_ascii=False)
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>PersonalMind 记忆网络</title>
    <script src="https://cdn.jsdelivr.net/npm/vis-network@9.1.6/standalone/umd/vis-network.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: white;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{
            text-align: center;
            padding: 30px 0;
        }}
        h1 {{ 
            font-size: 2.5em; 
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        .subtitle {{ color: #94a3b8; font-size: 1.1em; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(90deg, #00d4ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stat-label {{ color: #94a3b8; margin-top: 5px; font-size: 0.9em; }}
        .understanding-bar {{
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            height: 30px;
            margin: 20px 0;
            overflow: hidden;
            position: relative;
        }}
        .understanding-fill {{
            height: 100%;
            background: linear-gradient(90deg, #00d4ff, #7c3aed);
            border-radius: 20px;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}
        #network {{
            width: 100%;
            height: 500px;
            border-radius: 15px;
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        .tooltip {{
            position: absolute;
            background: rgba(30,30,50,0.95);
            padding: 15px;
            border-radius: 10px;
            max-width: 300px;
            border: 1px solid rgba(255,255,255,0.2);
            display: none;
            z-index: 1000;
        }}
        .tooltip h4 {{ color: #00d4ff; margin-bottom: 8px; }}
        .tooltip p {{ color: #ccc; font-size: 0.9em; line-height: 1.5; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧠 PersonalMind 记忆网络</h1>
            <p class="subtitle">你的 AI 大脑如何理解和记住你</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['total_memories']}</div>
                <div class="stat-label">记忆总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['by_type'].get('episodic', 0)}</div>
                <div class="stat-label">情景记忆</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['by_type'].get('semantic', 0)}</div>
                <div class="stat-label">语义记忆</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats['understanding']}%</div>
                <div class="stat-label">理解度</div>
            </div>
        </div>
        
        <div class="understanding-bar">
            <div class="understanding-fill" style="width: {stats['understanding']}%">
                AI 对你的理解程度
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-dot" style="background: #ff6b6b;"></div>
                <span>你（中心）</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: #ffd93d;"></div>
                <span>情景记忆</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: #6bcb77;"></div>
                <span>语义记忆</span>
            </div>
            <div class="legend-item">
                <div class="legend-dot" style="background: #4d96ff;"></div>
                <span>工作记忆</span>
            </div>
        </div>
        
        <div id="network"></div>
        
        <div class="tooltip" id="tooltip">
            <h4 id="tooltip-title"></h4>
            <p id="tooltip-content"></p>
        </div>
    </div>
    
    <script>
        var nodes = new vis.DataSet({nodes_json});
        
        var edges_data = [];
        var nodeMap = new Map();
        nodes.forEach(function(node) {{
            nodeMap.set(node.id, node);
        }});
        
        // Create edges from connections
        nodes.forEach(function(node) {{
            if (node.connections) {{
                node.connections.forEach(function(conn) {{
                    edges_data.push({{from: node.id, to: conn, color: {{opacity: 0.3}}}});
                }});
            }}
        }});
        
        var edges = new vis.DataSet(edges_data);
        
        var container = document.getElementById('network');
        var data = {{ nodes: nodes, edges: edges }};
        
        var options = {{
            nodes: {{
                shape: 'dot',
                size: 20,
                font: {{ size: 14, color: '#ffffff' }},
                borderWidth: 2,
                shadow: true
            }},
            edges: {{
                width: 2,
                color: {{ opacity: 0.4 }},
                smooth: {{ type: 'continuous' }}
            }},
            physics: {{
                stabilization: {{ iterations: 100 }},
                barnesHut: {{
                    gravitationalConstant: -2000,
                    centralGravity: 0.5,
                    springLength: 150,
                    springConstant: 0.04
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 200
            }}
        }};
        
        var network = new vis.Network(container, data, options);
        
        // Color nodes by type
        network.on('stabilizationIterationsDone', function() {{
            nodes.forEach(function(node) {{
                var color;
                if (node.type === 'user') {{
                    color = '#ff6b6b';
                }} else if (node.type === 'episodic') {{
                    color = '#ffd93d';
                }} else if (node.type === 'semantic') {{
                    color = '#6bcb77';
                }} else if (node.type === 'working') {{
                    color = '#4d96ff';
                }} else {{
                    color = '#gray';
                }}
                node.color = {{ background: color, border: color, highlight: {{ background: color, border: color }} }};
                // Size based on importance
                node.size = 15 + node.importance * 20;
            }});
            nodes.update(nodes.get());
        }});
        
        // Tooltip on hover
        var tooltip = document.getElementById('tooltip');
        var tooltipTitle = document.getElementById('tooltip-title');
        var tooltipContent = document.getElementById('tooltip-content');
        
        network.on('hoverNode', function(params) {{
            var node = nodes.get(params.node);
            tooltipTitle.textContent = node.label;
            tooltipContent.textContent = node.full_content + '\\n\\n创建时间: ' + node.created;
            tooltip.style.display = 'block';
            tooltip.style.left = params.event.pageX + 10 + 'px';
            tooltip.style.top = params.event.pageY + 10 + 'px';
        }});
        
        network.on('blurNode', function() {{
            tooltip.style.display = 'none';
        }});
    </script>
</body>
</html>
"""
        return html
    
    def save_html(self, filepath: str = "memory_network.html"):
        """保存为 HTML 文件"""
        html = self.generate_html()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        return filepath


# 全局可视化器实例
_visualizer: Optional[MemoryVisualizer] = None

def get_visualizer() -> MemoryVisualizer:
    """获取可视化器实例"""
    global _visualizer
    if _visualizer is None:
        _visualizer = MemoryVisualizer()
    return _visualizer

def reset_visualizer():
    """重置可视化器"""
    global _visualizer
    _visualizer = None


def demo():
    """演示"""
    print("=" * 50)
    print("PersonalMind 记忆可视化演示")
    print("=" * 50)
    
    viz = MemoryVisualizer()
    
    # 添加一些示例记忆
    print("\n添加示例记忆...")
    viz.add_memory("我叫李明，是一名软件工程师", "semantic", 0.9)
    viz.add_memory("我喜欢川菜和火锅", "semantic", 0.8)
    viz.add_memory("最近在做一个强化学习项目", "working", 0.7)
    viz.add_memory("下周三有个项目评审会议", "episodic", 0.8)
    viz.add_memory("每天早上跑步半小时", "semantic", 0.6)
    viz.add_memory("在学习 PyTorch 深度学习", "working", 0.7)
    
    # 显示统计
    stats = viz.get_stats()
    print(f"\n记忆统计:")
    print(f"  总数: {stats['total_memories']}")
    print(f"  理解度: {stats['understanding']}%")
    print(f"  高重要性: {stats['high_importance']}")
    
    # 生成 HTML
    output_path = viz.save_html("demo_memory_network.html")
    print(f"\n可视化已保存到: {output_path}")


if __name__ == "__main__":
    demo()
