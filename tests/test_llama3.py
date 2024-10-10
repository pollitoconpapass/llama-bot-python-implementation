import ollama
import json
import requests

MODEL_NAME = 'llama3.2:1b'
message_history = []  # -> just as an example guide (not really gonna be useful here)


# === CLASSSICAL LLAMA IMPLEMENTATION ===
def llama3_chat(question: str) -> str:
    message_history.append({"role": "user", "content": question})

    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in message_history])
    formatted_prompt = f"Question: {question}\n\nHistory: {history_str}"

    response = ollama.chat(model=MODEL_NAME, messages=[{'role': 'assistant', 'content': 'You\'re a helpful AI assistant'},
                                                       {'role': 'user', 'content': formatted_prompt}])
    message_history.append({"role": "assistant", "content": response['message']['content']})

    return response['message']['content']


# === OLLAMA API IMPLEMENTATION ===
def ollama_api(question: str) -> str:
    request = requests.post("http://localhost:11434/api/generate", json={"model": MODEL_NAME, "prompt": question})

    responses = [json.loads(line) for line in request.text.splitlines()]
    responses = [response["response"] for response in responses]

    answer = "".join(responses)
    return answer
    

# === STREAMING IMPLEMENTATION (without history) ===
def llama3_stream_chat(question: str) -> str:
    stream = ollama.chat(
        model='llama3.2:1b',
        messages=[
            {'role': 'assistant', 'content': 'You\'re a helpful AI assistant expert in WWII'},
            {'role': 'user', 'content': question}
        ],
        stream=True,
    )

    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)


# === MAIN ===
question = """Explain the Paris ocupation of WW2"""
answer = llama3_stream_chat(question)
# print(answer)
