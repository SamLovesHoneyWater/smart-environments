from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
#from langchain_community.tools.shell.tool import ShellTool

import subprocess
from langchain.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel

class ShellInput(BaseModel):
    command: str
    user_input: Optional[str] = None  # user can pass Y/N or other input if known

class SmartShellTool(BaseTool):
    name = "ubuntu_shell"
    description = (
        "Executes Ubuntu shell commands. Prompts the user if input is required. "
        "Supports interactive prompts like Y/N by passing stdin input."
    )
    args_schema: Type[BaseModel] = ShellInput

    def _run(self, command: str, user_input: Optional[str] = None, run_manager=None) -> str:
        print(f"\n🛠️ Agent wants to run:\n  {command}")
        allow = input("Authorize? [y/N]: ").strip().lower()
        if allow != "y":
            return "⛔ User denied the command."

        # Ask if user wants to auto-respond to prompt
        if not user_input and self._is_interactive(command):
            user_input = input("This command may ask for input (like Y/n). Auto-reply? [Y/n]: ").strip() or "Y"
            user_input += "\n"

        return self._run_command(command, user_input)

    def _is_interactive(self, command: str) -> bool:
        likely_prompts = ["apt install", "rm -i", "mv -i", "cp -i"]
        return any(trigger in command for trigger in likely_prompts)

    def _run_command(self, command: str, input_text: Optional[str] = None) -> str:
        try:
            proc = subprocess.Popen(
                command,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            output, _ = proc.communicate(input=input_text, timeout=20)
            return output.strip()
        except subprocess.TimeoutExpired:
            proc.kill()
            return "⏰ Command timed out."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _arun(self, command: str, user_input: Optional[str] = None, run_manager=None):
        raise NotImplementedError("Async not supported for SmartShellTool.")


def main():
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    shell_tool = SmartShellTool()
    agent = initialize_agent(
        tools=[shell_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

    while True:
        try:
            query = input("\n💬 Ask the agent: ")
            result = agent.run(query)
            print("\n🧠 Final Answer:", result)
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break

if __name__ == "__main__":
    main()
