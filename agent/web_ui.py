# PersonalMind Web UI
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.llm import PROVIDERS, get_llm
from agent.memory import get_memory


def create_web_ui():
    try:
        import gradio as gr
    except ImportError:
        return None
    
    llm = get_llm()
    memory = get_memory()
    
    # Build provider choices
    provider_choices = []
    for key, p in PROVIDERS.items():
        label = "%s" % p["name"]
        provider_choices.append((label, key))
    
    with gr.Blocks(title="PersonalMind", theme=gr.themes.Soft()) as app:
        gr.Markdown("# PersonalMind - Your AI Brain")
        gr.Markdown("Supports 10+ AI providers: DeepSeek, OpenAI, Qwen, Kimi, GLM, Claude, Gemini and more.")
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="Chat", height=450)
                msg_input = gr.Textbox(label="Message", placeholder="Type your message...", show_label=False)
                with gr.Row():
                    send_btn = gr.Button("Send", variant="primary")
                    clear_btn = gr.Button("Clear Chat")
            
            with gr.Column(scale=1):
                gr.Markdown("### Settings")
                
                provider_dropdown = gr.Dropdown(
                    choices=provider_choices,
                    value=llm.provider_key,
                    label="AI Provider"
                )
                
                model_dropdown = gr.Dropdown(
                    choices=PROVIDERS.get(llm.provider_key, {}).get("models", []),
                    value=llm.model,
                    label="Model",
                    allow_custom_value=True
                )
                
                api_key_input = gr.Textbox(
                    label="API Key",
                    type="password",
                    placeholder="Enter your API key..."
                )
                
                status_text = gr.Textbox(label="Status", interactive=False, value="")
                
                gr.Markdown("---")
                gr.Markdown("### Commands")
                gr.Markdown("/help /search /remember\n/forget /memory /stats")
                
                gr.Markdown("---")
                mem_btn = gr.Button("View Memories")
                mem_text = gr.Textbox(label="Memories", interactive=False, lines=8)
        
        # Provider change -> update model list
        def on_provider_change(provider_key):
            p = PROVIDERS.get(provider_key, {})
            models = p.get("models", [])
            default = p.get("default_model", "")
            website = p.get("website", "Set your API key below")
            return gr.update(choices=models, value=default), website
        
        provider_dropdown.change(
            on_provider_change,
            inputs=[provider_dropdown],
            outputs=[model_dropdown, status_text]
        )
        
        # Save settings & update status
        def on_save_settings(provider_key, model, api_key):
            llm.switch_provider(provider_key, api_key=api_key, model=model)
            info = llm.get_current_info()
            status = "Provider: %s\nModel: %s\nAPI Key: %s" % (
                info["provider_name"],
                info["model"],
                "Set" if info["has_key"] else "NOT SET"
            )
            return status
        
        api_key_input.change(
            on_save_settings,
            inputs=[provider_dropdown, model_dropdown, api_key_input],
            outputs=[status_text]
        )
        
        model_dropdown.change(
            on_save_settings,
            inputs=[provider_dropdown, model_dropdown, api_key_input],
            outputs=[status_text]
        )
        
        # Chat
        def respond(message, history):
            if not message.strip():
                return "", history
            
            # Apply settings before chatting
            on_save_settings(provider_dropdown.value, model_dropdown.value, api_key_input.value)
            
            response = llm.chat(message)
            history.append((message, response))
            return "", history
        
        send_btn.click(respond, [msg_input, chatbot], [msg_input, chatbot])
        msg_input.submit(respond, [msg_input, chatbot], [msg_input, chatbot])
        
        # Clear
        def clear():
            llm.clear_history()
            return [], []
        
        clear_btn.click(clear, [], [chatbot, msg_input])
        
        # Memory view
        def show_memory():
            stats = memory.get_memory_stats()
            all_mem = memory.get_all_memories()
            text = "Total: %d items\n\n" % stats["total"]
            for mem_type, mems in all_mem.items():
                if mems:
                    text += "[%s] %d items\n" % (mem_type.title(), len(mems))
                    for m in mems[:5]:
                        text += "  - %s\n" % m["content"][:60]
                    text += "\n"
            return text if stats["total"] > 0 else "No memories yet. Chat to start!"
        
        mem_btn.click(show_memory, [], mem_text)
        
        # Init status
        info = llm.get_current_info()
        initial_status = "Provider: %s\nModel: %s\nAPI Key: %s" % (
            info["provider_name"],
            info["model"],
            "Set" if info["has_key"] else "NOT SET - Enter key on the right"
        )
        status_text.value = initial_status
        model_dropdown.choices = PROVIDERS.get(llm.provider_key, {}).get("models", [])
        model_dropdown.value = llm.model
    
    return app


def launch_ui(share=False, port=7860):
    app = create_web_ui()
    if app is None:
        print("Error: Gradio not installed. Run: pip install gradio")
        print("Try CLI mode instead: python main.py --cli")
        return
    print("Starting PersonalMind Web UI...")
    print("Open: http://localhost:%d" % port)
    app.launch(server_name="0.0.0.0", server_port=port, share=share)
