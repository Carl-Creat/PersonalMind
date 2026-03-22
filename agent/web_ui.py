"""
PersonalMind Web UI
基于 Gradio 的网页界面
"""
import gradio as gr
from typing import Tuple

from agent.core import get_agent
from agent.memory import get_memory


def create_web_ui() -> gr.Blocks:
    """创建 Web UI"""
    
    agent = get_agent()
    
    # CSS 样式
    css = """
    .container {
        max-width: 800px;
        margin: auto;
    }
    .welcome-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .stats-box {
        background: #f5f5f5;
        padding: 15px;
        border-radius: 8px;
        margin-top: 20px;
    }
    """
    
    with gr.Blocks(css=css, title="PersonalMind - 你的私人 AI 大脑") as app:
        gr.Markdown("""
        # 🧠 PersonalMind
        ### 你的私人 AI 大脑
        """)
        
        # 欢迎框
        gr.Markdown("""
        <div class="welcome-box">
        <b>欢迎使用 PersonalMind！</b><br>
        我能记住你的偏好、联网搜索信息、帮你完成任务。<br>
        直接和我对话即可，我会自动记住重要信息。
        </div>
        """)
        
        # 对话框
        chatbot = gr.Chatbot(
            label="对话历史",
            height=400,
            show_copy_button=True
        )
        
        # 输入框
        msg_input = gr.Textbox(
            label="输入消息",
            placeholder="输入你的问题或命令...",
            lines=2
        )
        
        # 按钮行
        with gr.Row():
            submit_btn = gr.Button("发送", variant="primary")
            clear_btn = gr.Button("清空对话")
        
        # 记忆面板
        with gr.Accordion("📚 记忆管理", open=False):
            gr.Markdown("##### 记忆统计")
            memory_stats = gr.JSON(label="统计")
            
            with gr.Row():
                show_mem_btn = gr.Button("查看所有记忆")
                clear_mem_btn = gr.Button("清空记忆")
            
            memory_display = gr.JSON(label="记忆列表")
        
        # 命令帮助
        with gr.Accordion("📖 命令帮助", open=False):
            gr.Markdown("""
            **可用命令：**
            - `/search <关键词>` - 联网搜索
            - `/remember <内容>` - 记住信息
            - `/forget <关键词>` - 删除记忆
            - `/memory` - 查看所有记忆
            - `/clear` - 清空对话历史
            - `/stats` - 查看使用统计
            
            **也可以直接对话，AI 会自动记住重要信息！**
            """)
        
        # 事件处理
        def respond(message: str, history: list) -> Tuple:
            """处理用户输入"""
            if not message.strip():
                return "", history
            
            # 获取 AI 回复
            response = agent.chat(message)
            
            # 添加到历史
            history.append((message, response))
            
            return "", history
        
        def clear_conversation():
            """清空对话"""
            agent.llm.clear_history()
            return None, []
        
        def update_memory_stats():
            """更新记忆统计"""
            memory = get_memory()
            return memory.get_memory_stats()
        
        def show_all_memories():
            """显示所有记忆"""
            memory = get_memory()
            all_mem = memory.get_all_memories()
            return all_mem
        
        def clear_all_memories():
            """清空所有记忆"""
            memory = get_memory()
            memory.memory.db.clear()
            return {"message": "记忆已清空"}, {}
        
        # 绑定事件
        submit_btn.click(
            fn=respond,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot]
        )
        
        msg_input.submit(
            fn=respond,
            inputs=[msg_input, chatbot],
            outputs=[msg_input, chatbot]
        )
        
        clear_btn.click(
            fn=clear_conversation,
            outputs=[msg_input, chatbot]
        )
        
        show_mem_btn.click(
            fn=update_memory_stats,
            outputs=[memory_stats]
        )
        
        show_mem_btn.click(
            fn=show_all_memories,
            outputs=[memory_display]
        )
        
        clear_mem_btn.click(
            fn=clear_all_memories,
            outputs=[memory_stats, memory_display]
        )
        
        # 初始化
        app.load(
            fn=update_memory_stats,
            outputs=[memory_stats]
        )
    
    return app


def launch_ui(share: bool = False, port: int = 7860):
    """启动 UI"""
    app = create_web_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=share
    )
