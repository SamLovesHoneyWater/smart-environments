import os
import subprocess
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.chat_models import ChatOpenAI
from langchain.tools.base import BaseTool
from typing import Optional
from pydantic import BaseModel

# Restricted shell commands
ALLOWED_COMMANDS = ['ls', 'pwd', 'whoami', 'uname', 'date', 'uptime', 'df', 'free', 'echo']

class ShellInput(BaseModel):
    command: str

class SecureShellTool(BaseTool):
    name = "ubuntu_shell"
    description = "Use this to run safe Ubuntu shell commands. Input should be a single shell command string."
    args_schema = ShellInput

    def _run(self, command: str, run_manager=None):
        cmd = command.strip()
        if cmd.split()[0] not in ALLOWED_COMMANDS:
            return "❌ Command not allowed."
        
        # Prompt for user authorization
        print(f"\n🛠️ The agent wants to run: `{cmd}`")
        allow = input("Authorize? [y/N]: ").strip().lower()
        if allow not in ["y", "yes"]:
            return "⛔ Command execution denied by user."

        try:
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            return result.strip()
        except subprocess.CalledProcessError as e:
            return f"❌ Error: {e.output.strip()}"

    def _arun(self, command: str, run_manager=None):
        raise NotImplementedError("Async not supported for shell tool.")

def main():
    llm = ChatOpenAI(model="gpt-4", temperature=0)

    shell_tool = SecureShellTool()
    tools = [shell_tool]

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
    )

    print("💬 Ask your question (Ctrl+C to quit):")
    while True:
        try:
            query = input("\nYou: ")
            agent.run(query)
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
