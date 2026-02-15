from ollama_engine import ask_llm

question = "Is the environment safe right now?"
response = ask_llm(question)

print("\nAI RESPONSE:\n")
print(response)