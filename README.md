# PersonalMind - 你的私人 AI 大脑 🧠

> 开箱即用的本地 AI 助手，能记忆你的偏好、能联网搜索、能帮你完成任务

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Demo](docs/demo.gif)

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🧠 **长期记忆** | 记住你的偏好、习惯、重要信息，越用越懂你 |
| 🔍 **联网搜索** | 实时搜索最新信息，不再局限于训练数据 |
| 💻 **任务执行** | 帮你执行电脑操作、写代码、发消息 |
| 🔒 **本地运行** | 数据留在本地，保护隐私 |
| 🌐 **网页界面** | 简洁美观的 Web UI，随时访问 |
| 🔧 **可扩展** | 轻松添加新工具和新能力 |

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- OpenAI API Key（或兼容的 LLM API）

### 安装

```bash
# 克隆仓库
git clone https://github.com/Carl-Creat/PersonalMind.git
cd PersonalMind

# 安装依赖
pip install -r requirements.txt

# 启动
python main.py
```

然后打开浏览器访问 `http://localhost:7860`

### 配置

在 `config.py` 或环境变量中设置：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-4"  # 或 gpt-3.5-turbo
```

---

## 📖 使用指南

### 首次使用

1. 启动后，在网页中输入你的基本信息（姓名、职业、兴趣等）
2. AI 会记住这些信息，下次对话时会自动使用
3. 开始对话吧！

### 对话示例

```
你: 帮我搜索一下今天有什么科技新闻
AI: [联网搜索中...] 
    今天科技头条：
    1. xxx
    2. xxx
    ...

你: 帮我记住我下周三有个会议
AI: 已记住！你下周三有个会议。届时我可以提醒你。

你: 我的项目进度怎么样了？
AI: 根据我们的对话记录，你最近在完善...
```

### 可用命令

| 命令 | 功能 |
|------|------|
| `/search <关键词>` | 联网搜索 |
| `/remember <内容>` | 让 AI 记住信息 |
| `/forget <关键词>` | 删除记忆 |
| `/memory` | 查看所有记忆 |
| `/clear` | 清空对话历史 |
| `/help` | 显示帮助 |

---

## 🏗️ 项目结构

```
PersonalMind/
├── main.py              # 程序入口
├── config.py            # 配置文件
├── requirements.txt     # 依赖
│
├── agent/
│   ├── __init__.py
│   ├── core.py          # 核心 Agent
│   ├── memory.py        # 记忆系统
│   ├── tools.py         # 工具集
│   ├── llm.py           # LLM 接口
│   └── web_ui.py        # 网页界面
│
├── data/                # 数据存储
│   └── memory.db        # SQLite 数据库
│
├── docs/                # 文档
│   ├── demo.gif
│   └── tutorial.md
│
└── examples/            # 示例
    └── conversation.md
```

---

## 🧠 记忆系统

PersonalMind 的记忆系统分为三层：

```
┌─────────────────────────────────────┐
│     情景记忆 (Episodic Memory)       │
│     对话历史、事件序列              │
├─────────────────────────────────────┤
│     语义记忆 (Semantic Memory)      │
│     事实、知识、偏好                │
├─────────────────────────────────────┤
│     工作记忆 (Working Memory)       │
│     当前任务、临时信息              │
└─────────────────────────────────────┘
```

### 记忆检索

当你说话时，AI 会自动检索相关记忆，让回复更个性化：

```
你: 我喜欢吃川菜
[记忆检索] 找到: 用户偏好 -> 川菜
AI: 好的！我记住你喜欢川菜了，下次推荐餐厅会考虑这个。
```

---

## 🔧 工具集

### 已实现

| 工具 | 功能 |
|------|------|
| `web_search` | 联网搜索最新信息 |
| `calculator` | 数学计算 |
| `file_operations` | 文件读写 |
| `web_scraper` | 网页内容抓取 |
| `code_executor` | 执行代码片段 |

### 扩展工具

在 `agent/tools.py` 中添加新工具：

```python
@register_tool
def custom_tool(query: str) -> str:
    """自定义工具描述"""
    # 你的工具逻辑
    return result
```

---

## 🤝 贡献

欢迎贡献代码！

1. Fork 本仓库
2. 创建新分支
3. 提交代码
4. 创建 Pull Request

---

## 📝 更新日志

### 2026-03-22
- 初始化项目
- 实现核心 Agent 架构
- 实现三层记忆系统
- 实现基础工具集
- 开发 Web UI 界面

---

## 📚 学习资源

- [LangChain 文档](https://docs.langchain.com/)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Gradio 教程](https://gradio.app/docs/)

---

## License

MIT License

---

*让 AI 真正懂你，成为你的第二大脑* 🧠
