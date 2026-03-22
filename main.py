"""
PersonalMind 主程序

用法:
    python main.py                 # 启动 Web UI
    python main.py --cli           # 命令行模式
    python main.py --api           # API 模式
"""
import os
import sys
import argparse

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OPENAI_API_KEY, WEB_UI_PORT, WEB_UI_SHARE


def main():
    parser = argparse.ArgumentParser(description="PersonalMind - 你的私人 AI 大脑")
    parser.add_argument("--cli", action="store_true", help="命令行模式")
    parser.add_argument("--api", action="store_true", help="API 模式")
    parser.add_argument("--port", type=int, default=WEB_UI_PORT, help="Web UI 端口")
    parser.add_argument("--share", action="store_true", help="创建公开链接")
    args = parser.parse_args()
    
    # 检查 API Key
    if not OPENAI_API_KEY:
        print("""
╔══════════════════════════════════════════════════════════════╗
║                      ⚠️  重要提示                           ║
╠══════════════════════════════════════════════════════════════╣
║  请设置 OPENAI_API_KEY                                       ║
║                                                              ║
║  方法1: 创建 .env 文件                                       ║
║      echo OPENAI_API_KEY=your-key > .env                      ║
║                                                              ║
║  方法2: 设置环境变量                                          ║
║      export OPENAI_API_KEY=your-key                         ║
║                                                              ║
║  获取 API Key: https://platform.openai.com/api-keys          ║
╚══════════════════════════════════════════════════════════════╝
        """)
        sys.exit(1)
    
    if args.cli:
        # 命令行模式
        run_cli()
    elif args.api:
        # API 模式
        run_api()
    else:
        # Web UI 模式
        run_web_ui(args.port, args.share)


def run_cli():
    """命令行交互模式"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                  🧠 PersonalMind CLI 模式                     ║
║                  你的私人 AI 大脑                            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    from agent.core import get_agent
    
    agent = get_agent()
    print(agent.get_welcome_message())
    
    while True:
        try:
            user_input = input("\n你: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\n再见！👋")
                break
            
            response = agent.chat(user_input)
            print(f"\nAI: {response}")
            
        except KeyboardInterrupt:
            print("\n\n再见！👋")
            break
        except Exception as e:
            print(f"\n错误：{str(e)}")


def run_api():
    """API 服务模式"""
    print("启动 API 服务...")
    # 这里可以添加 FastAPI 等框架
    print("API 模式开发中...")


def run_web_ui(port: int, share: bool):
    """Web UI 模式"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                  🧠 PersonalMind Web UI                      ║
║                  你的私人 AI 大脑                            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  启动中...                                                   ║
║                                                              ║
║  访问: http://localhost:{port}                               ║
    """)
    
    if share:
        print("""
║  公开链接: 创建中...                                          ║
        """)
    
    print("╚══════════════════════════════════════════════════════════════╝")
    
    from agent.web_ui import launch_ui
    launch_ui(share=share, port=port)


if __name__ == "__main__":
    main()
