import openai
import subprocess
import os
import time

openai.api_key = os.getenv("OPENAI_API_KEY") or "your-api-key"


def execute_command(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"❌ Error: {e.output.strip()}"

def ask_user_permission(command):
    print(f"\n🛠️  Agent wants to run: `{command}`")
    user_input = input("Authorize? [y/N]: ").strip().lower()
    return user_input in ['y', 'yes']

def run_react_loop(user_input, time_limit_seconds=60):
    history = [
        {"role": "system", "content": "You are a REACT agent with access to a Linux terminal. Use Thought/Action/Observation format. Terminate when task is complete using 'Final Answer:'."},
        {"role": "user", "content": user_input}
    ]

    start_time = time.time()

    while True:
        if time.time() - start_time > time_limit_seconds:
            print("⏱️ Time limit reached.")
            break

        # Ask OpenAI for next reasoning step
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=history,
            temperature=0.3,
        )
        reply = response.choices[0].message.content.strip()
        print("\n🤖 Agent:\n" + reply)
        history.append({"role": "assistant", "content": reply})

        # Check if it's a final answer
        if "Final Answer:" in reply:
            print("\n✅ Task completed.")
            break

        # Check for an Action line
        action_line = next((line for line in reply.splitlines() if line.lower().startswith("action:")), None)
        if action_line:
            command = action_line.split(":", 1)[1].strip().lstrip("<").rstrip(">")
            if not ask_user_permission(command):
                observation = "❌ User denied permission to execute the command."
                print(observation)
            else:
                observation = execute_command(command)
                print("\n🔎 Observation:\n" + observation)

            # Feed observation back to the model
            history.append({"role": "user", "content": f"Observation: {observation}"})

if __name__ == "__main__":
    print("🔁 REACT Agent CLI — Ubuntu Tool Use with LLM Reasoning")
    query = input("💬 What's your question for the agent? ")
    run_react_loop(query)
