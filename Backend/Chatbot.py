import json
from groq import Groq
from dotenv import dotenv_values
import datetime

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Handle reading and initializing an empty list for the messages file
try:
    with open(r"Data\ChatLog.json", "r") as f:
        content = f.read().strip()
        if content:
            messages = json.loads(content)
        else:
            messages = []  # Initialize as an empty list if the file is empty
except (json.JSONDecodeError, FileNotFoundError):
    messages = []  # Initialize as an empty list if file doesn't exist or is empty

def RealtimeInformation():
    curr_date_time = datetime.datetime.now()
    day = curr_date_time.strftime("%A")
    date = curr_date_time.strftime("%d")
    month = curr_date_time.strftime("%B")
    year = curr_date_time.strftime("%Y")
    hour = curr_date_time.strftime("%H")
    minute = curr_date_time.strftime("%M")
    second = curr_date_time.strftime("%S")

    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def ChatBot(Query):
    try:
        messages.append({"role": "user", "content": f"{Query}"})

        # Non-streaming mode for easier debugging
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=False
        )

        # Correctly access the response content using object attributes
        if completion.choices and len(completion.choices) > 0:
            Answer = completion.choices[0].message.content
        else:
            Answer = "Sorry, I couldn't generate a response."
        
        Answer = Answer.replace("</s>", "")  # Clean up the output

        messages.append({"role": "assistant", "content": Answer})

        # Save the messages to the JSON file
        with open(r"Data\ChatLog.json", "w") as f:
            json.dump(messages, f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")
        with open(r"Data\ChatLog.json", "w") as f:
            json.dump(messages, f, indent=4)
        return f"An error occurred: {str(e)}"
        return ChatBot(Query)

if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        if user_input.lower() in ["exit", "quit", "close"]:
            print("Exiting the chatbot...")
            break
        print(ChatBot(user_input))
