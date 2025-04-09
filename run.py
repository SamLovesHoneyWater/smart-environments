from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain_community.tools.shell.tool import ShellTool
from langchain.memory import ConversationBufferMemory

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
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent = initialize_agent(
        tools=[shell_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        memory=memory,
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
