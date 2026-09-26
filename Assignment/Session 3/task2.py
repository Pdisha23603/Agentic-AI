# -------- SHORT-TERM MEMORY CHATBOT --------

memory = []

while True:

    message = input("You: ")

    # Exit the chatbot
    if message.lower() == "exit":
        print("Chatbot: Exiting the program... Goodbye!")
        break

    # Repeat last 3 messages
    elif message.lower() == "repeat":
        print("Chatbot: Your last 3 messages are:")
        for msg in memory:
            print("-", msg)

    # Store new message
    else:
        memory.append(message)

        # Keep only the last 3 messages
        if len(memory) > 3:
            memory.pop(0)

        print("Chatbot: I remember your message.")





# output:
# PS C:\Users\disha\agentic ai\Tops task\Assignment\Session 3> & C:\Users\disha\AppData\Local\Programs\Python\Python314\python.exe "c:/Users/disha/agentic ai/Tops task/Assignment/Session 3/task2.py"
# You: hello 
# Chatbot: I remember your message.
# You: how are you dear
# Chatbot: I remember your message.
# You: i like burger and pizza 
# Chatbot: I remember your message.
# You: can you suggest me the best place for it
# Chatbot: I remember your message.
# You: repeat
# Chatbot: Your last 3 messages are:
# - how are you dear
# - i like burger and pizza 
# - can you suggest me the best place for it
# You: exit
# Chatbot: Exiting the program... Goodbye!
# PS C:\Users\disha\agentic ai\Tops task\Assignment\Session 3> & C:\Users\disha\AppData\Local\Programs\Python\Python314\python.exe "c:/Users/disha/agentic ai/Tops task/Assignment/Session 3/task2.py"