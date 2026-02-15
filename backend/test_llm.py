from llm_engine import ask_llm

question = "Is the room environment comfortable right now?"
answer = ask_llm(question)

print("\nLLM RESPONSE:\n")
print(answer)