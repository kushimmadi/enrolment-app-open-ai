import os

from openai import OpenAI

from services.prompt_loader import load_lab4_prompt


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")

client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")


def create_chat_completion(messages, max_tokens=300, temperature=0.2, model=None):
    response = client.chat.completions.create(
        model=model or OLLAMA_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content


def call_architecture_agent(system_prompt_file, task_prompt_file, user_input, max_tokens=300):
    system_prompt = load_lab4_prompt(system_prompt_file)
    task_prompt = load_lab4_prompt(task_prompt_file)

    final_prompt = f"""
{task_prompt}

User Input:

{user_input}
"""

    answer = create_chat_completion(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": final_prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.2,
    )
    return answer.strip()
