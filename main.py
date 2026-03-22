# PersonalMind - Your Personal AI Brain
from __future__ import print_function
import os
import sys
import argparse

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from config import OPENAI_API_KEY, WEB_UI_PORT, WEB_UI_SHARE


def main():
    parser = argparse.ArgumentParser(description="PersonalMind - Your AI Brain")
    parser.add_argument("--cli", action="store_true", help="Command line mode")
    parser.add_argument("--api", action="store_true", help="API mode")
    parser.add_argument("--port", type=int, default=WEB_UI_PORT, help="Web UI port")
    parser.add_argument("--share", action="store_true", help="Create public link")
    args = parser.parse_args()
    
    if not OPENAI_API_KEY:
        print("=" * 50)
        print("PersonalMind - Setup Required")
        print("=" * 50)
        print("Please set OPENAI_API_KEY in .env file")
        print("Get API Key: https://platform.openai.com/api-keys")
        print("=" * 50)
        sys.exit(1)
    
    if args.cli:
        run_cli()
    elif args.api:
        run_api()
    else:
        run_web_ui(args.port, args.share)


def run_cli():
    print("\n=== PersonalMind CLI Mode ===\n")
    
    from agent.core import get_agent
    
    agent = get_agent()
    print(agent.get_welcome_message())
    
    running = True
    while running:
        try:
            try:
                user_input = raw_input("\nYou: ").strip()
            except NameError:
                user_input = input("\nYou: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye!")
                running = False
            else:
                try:
                    response = agent.chat(user_input)
                    print("\nAI: " + response)
                except Exception as e:
                    print("\nError: " + str(e))
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            running = False


def run_api():
    print("API mode - Coming soon...")


def run_web_ui(port, share):
    print("\n=== PersonalMind Web UI ===")
    print("Starting server...")
    print("Open: http://localhost:" + str(port))
    print("")
    
    from agent.web_ui import launch_ui
    launch_ui(share=share, port=port)


if __name__ == "__main__":
    main()
