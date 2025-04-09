import openai
import subprocess

# Set your OpenAI key
openai.api_key = "your-api-key"

# Define allowed commands for safety
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
You are a REACT agent with access to an Ubuntu command line. Think step-by-step and act only when needed.
Format:
Thought: ...
Action: ...
Observation: ...

Now, given the user's query: "{user_input}", reason and decide what to do.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        temperature=0.2
    )

    output = response['choices'][0]['message']['content']
    print("\nAgent Output:\n", output)

    # Look for Action line and execute it
    for line in output.splitlines():
        if line.strip().lower().startswith("action:"):
            cmd = line.split(":", 1)[1].strip()
            obs = execute_command(cmd)
            print("\nObservation:\n", obs)
            return

if __name__ == "__main__":
    while True:
        user_query = input("💬 Your question (type 'exit' to quit): ")
        if user_query.lower() in ['exit', 'quit']:
            break
        react_agent(user_query)
