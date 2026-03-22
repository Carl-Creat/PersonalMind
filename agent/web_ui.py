# PersonalMind Web UI
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_web_ui():
    try:
        import gradio as gr
    except ImportError:
        return None
    
    from agent.core import get_agent
    from agent.memory import get_memory
    
    agent = get_agent()
    
    with gr.Blocks(title="PersonalMind") as app:
        gr.Markdown("# PersonalMind - Your AI Brain")
        gr.Markdown("Your personal AI assistant with memory")
        
        chatbot = gr.Chatbot(label="Conversation", height=400)
        msg_input = gr.Textbox(label="Message", placeholder="Type your message...")
        
        def respond(message, history):
            if not message.strip():
                return "", history
            response = agent.chat(message)
            history.append((message, response))
            return "", history
        
        def clear():
            agent.llm.clear_history()
            return None, []
        
        def show_memory():
            memory = get_memory()
            stats = memory.get_memory_stats()
            all_mem = memory.get_all_memories()
            text = "Memory Statistics: " + str(stats["total"]) + " items\n\n"
            for mem_type, mems in all_mem.items():
                if mems:
                    text += mem_type.title() + ": " + str(len(mems)) + " items\n"
            return text
        
        gr.Button("Send").click(respond, [msg_input, chatbot], [msg_input, chatbot])
        gr.Button("Clear").click(clear, [], [msg_input, chatbot])
        
        with gr.Accordion("Memory", open=False):
            gr.Button("View Memories").click(show_memory, [], gr.Textbox(label="Memory", interactive=False))
    
    return app


def launch_ui(share=False, port=7860):
    app = create_web_ui()
    if app is None:
        print("Error: Gradio not installed. Run: pip install gradio")
        return
    print("Starting PersonalMind Web UI...")
    print("Open: http://localhost:" + str(port))
    app.launch(server_name="0.0.0.0", server_port=port, share=share)
