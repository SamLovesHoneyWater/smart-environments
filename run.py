import subprocess
import openai
import os

# Set your OpenAI API key (you can also use environment variable OPENAI_API_KEY)
openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key"

# Safety: allow only safe commands
ALLOWED_COMMANDS = ['ls', 'pwd', 'whoami', 'uname', 'date', 'uptime', 'df', 'free', 'echo']

def is_safe_command(cmd):
    return cmd.split()[0] in ALLOWED_COMMANDS

def execute_command(cmd):
    if not is_safe_command(cmd):
        return "⚠️ Command not allowed."
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"❌ Error: {e.output.strip()}"

def react_agent(user_input):
    prompt = f"""
You are a REACT agent with access to a Linux command line.
You must think step-by-step and use the terminal only when needed.

Use this format:

Thought: ...
Action: <ubuntu shell command>
Observation: ...

Now handle this user query: "{user_input}"
"""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant with terminal access."},
                  {"role": "user", "content": prompt}],
        temperature=0.2
    )

    output = response.choices[0].message.content
    print("\nAgent Output:\n", output)

    for line in output.splitlines():
        if line.lower().startswith("action:"):
            cmd = line.split(":", 1)[1].strip().lstrip("<").rstrip(">")
            obs = execute_command(cmd)
            print("\nObservation:\n", obs)
            return

if __name__ == "__main__":
    while True:
        user_query = input("💬 Your question (type 'exit' to quit): ")
        if user_query.lower() in ['exit', 'quit']:
            break
        react_agent(user_query)
