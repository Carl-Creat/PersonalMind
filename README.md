# PersonalMind - 你的私人 AI 大脑 🧠

> 开箱即用的本地 AI 助手，能记忆、能搜索、能执行任务、还能语音对话

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![Memory Network Demo](docs/memory_demo.gif)

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🧠 **三层记忆系统** | 情景/语义/工作记忆，越用越懂你 |
| 🔍 **联网搜索** | 实时搜索最新信息 |
| 👥 **多 Agent 协作** | 4 个 AI 助手团队协作 |
| 🎤 **语音交互** | 说话就能控制，不用打字 |
| 📄 **文件理解** | 扔图片/PDF/链接，AI 自动分析 |
| 🕸️ **记忆可视化** | 漂亮的记忆网络图，一眼看懂 AI 在想什么 |
| 🌐 **网页界面** | 简洁美观的 Web UI |
| 🔧 **可扩展** | 轻松添加新工具和新能力 |

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/Carl-Creat/PersonalMind.git
cd PersonalMind

# 安装依赖
pip install -r requirements.txt

# 配置（复制示例文件并填入你的 API Key）
cp .env.example .env
# 编辑 .env 文件，设置 OPENAI_API_KEY
```

### 启动

```bash
# Web UI 模式（推荐）
python main.py

# 命令行模式
python main.py --cli
```

然后打开浏览器访问 `http://localhost:7860`

---

## 🎯 功能演示

### 🧠 记忆系统

PersonalMind 会自动记住你说过的每一件重要的事：

```
你: 我喜欢吃川菜
AI: 已记住！我注意到你喜欢川菜，下次推荐餐厅会考虑这个。

你: 下周三有个重要会议
AI: 已记住！下周三你有重要会议，我会提醒你的。

你: /memory
【记忆列表】
- 你喜欢吃川菜 (重要性: 高)
- 下周三有重要会议 (重要性: 高)
```

### 👥 多 Agent 团队

不只是"一个 AI"，而是"一个团队"：

```
你: 帮我策划一个产品发布会
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🤖 **PersonalMind 团队响应**

🔍 研究员: 我来搜索一下最近成功的产品发布会案例...
📊 数据分析：发现 A 公司使用沉浸式体验提升了 40% 的参与度

🏠 管家: 从日程角度，建议安排在周末下午，参会者精力充沛

💡 创意师: 可以考虑加入互动装置，让嘉宾参与其中

💻 开发者: 技术层面可以用 AR 增强现场体验
```

### 🎤 语音交互

```bash
# 安装语音依赖
pip install edge-tts

# 对它说话，不用打字
python main.py --voice
```

### 📄 文件理解

```
你: [上传了一张截图]
AI: 【图片分析】
    
描述：这是一张 Python 代码截图
发现的文字：import torch, numpy as np...
    
详细分析：代码展示了 PyTorch 和 NumPy 的导入，
这是深度学习项目的基础配置。建议可以进一步分析
代码结构和可能的优化方向。

标签：代码、截图、Python
```

### 🕸️ 记忆可视化

打开内置的记忆可视化，看看 AI 是如何记住你的：

![Memory Network](docs/memory_network.png)

---

## 🏗️ 项目结构

```
PersonalMind/
├── main.py                 # 程序入口
├── config.py              # 配置文件
├── requirements.txt       # 依赖列表
├── README.md
│
├── agent/
│   ├── __init__.py
│   ├── core.py            # 核心 Agent
│   ├── memory.py          # 三层记忆系统
│   ├── visualization.py   # 记忆可视化
│   ├── multi_agent.py     # 多 Agent 团队
│   ├── voice.py           # 语音交互
│   ├── file_understanding.py  # 文件/图片理解
│   ├── llm.py             # LLM 接口
│   ├── tools.py           # 工具集
│   └── web_ui.py          # 网页界面
│
├── data/                  # 数据存储
│   └── memory.db         # SQLite 记忆库
│
└── docs/                 # 文档
    ├── demo.gif
    └── memory_network.png
```

---

## 🔧 可用命令

| 命令 | 功能 |
|------|------|
| `/search <词>` | 联网搜索 |
| `/remember <内容>` | 让 AI 记住信息 |
| `/forget <词>` | 删除相关记忆 |
| `/memory` | 查看所有记忆 |
| `/network` | 查看记忆可视化 |
| `/clear` | 清空对话历史 |
| `/team` | 查看多 Agent 团队 |
| `/help` | 显示帮助 |

---

## 🤝 贡献

欢迎贡献代码！

1. Fork 本仓库
2. 创建新分支 (`git checkout -b feature/新功能`)
3. 提交代码
4. 创建 Pull Request

---

## 📝 更新日志

### 2026-03-22
- ✅ 多 Agent 协作系统（4 个专业 AI 助手）
- ✅ 语音交互（STT + TTS）
- ✅ 文件/图片理解（GPT-4V 支持）
- ✅ 记忆可视化（漂亮的网络图）
- ✅ 重构项目结构

### 2026-03-22 (初始)
- 🎉 基础版本发布
- 🧠 三层记忆系统
- 🔍 联网搜索
- 🌐 Web UI

---

## 📚 学习资源

- [LangChain 文档](https://docs.langchain.com/)
- [OpenAI API](https://platform.openai.com/docs)
- [Gradio 教程](https://gradio.app/docs/)
- [Vis.js Network](https://visjs.org/)

---

## License

MIT License

---

*让 AI 真正懂你，成为你的第二大脑* 🧠
