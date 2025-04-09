from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain_community.tools.shell.tool import ShellTool

# Wrap with authorization logic
class SafeShellTool(ShellTool):
    def _run(self, command: str, run_manager=None):
        #allowed = ["ls", "pwd", "whoami", "uname", "date", "uptime", "df", "free", "echo"]
        disallowed = ["git", "rm", "mv", "chmod", "chown", "sudo", "curl", "wget", "ssh", "scp"]
        if command.split()[0] in disallowed:
            return "❌ Command not allowed."

        print(f"\n🛠️ Agent wants to run: `{command}`")
        if input("Allow? [y/N]: ").strip().lower() not in ["y", "yes"]:
            return "❌ User denied."

        return super()._run(command, run_manager)

def main():
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    shell_tool = SafeShellTool()
    agent = initialize_agent(
        tools=[shell_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )

    chat_history = []

    while True:
        try:
            query = input("\n💬 Ask the agent: ")
            chat_history.append({"role": "user", "content": query})
            result = agent.run(input=query, chat_history=chat_history)
            chat_history.append({"role": "assistant", "content": result})
            print("\n🧠 Final Answer:", result)
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break

if __name__ == "__main__":
    main()
