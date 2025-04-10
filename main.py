from utils import handle_query

def start():
    print("Starting agent...")

    conversation_history = [
        {
            'role': 'system', 
            'content': """
            You are an expert college advisor helping students explore engineering colleges in India.
            Focus exclusively on Indian institutes like IITs, NITs. Use prior messages in this conversation 
            to infer ambiguous terms like "there" or "it".
            """
        }
    ]

    initial_prompt = "Start the conversation with a friendly greeting."
    response, conversation_history = handle_query(initial_prompt, conversation_history)
    print(f"\nAgent: {response}\n{'-'*50}\n")

#USER LOOP
    print("Type 'exit' or 'quit' to end the conversation.")
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit", "end", "bye"]:
            print("Goodbye!")
            break

        response, conversation_history = handle_query(query, conversation_history)
        print(f"\nAgent: {response}\n{'-'*50}\n")


start()
