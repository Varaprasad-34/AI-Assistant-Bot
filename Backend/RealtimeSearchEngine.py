import json
from googlesearch import search
from groq import Groq
from json import dumps, load
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")


Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""
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

def GoogleSearch(query):
     result = list(search(query, advanced=True, num_results=5))
     Answer = f"The search result for '{query}' are:\n[start]\n"
     for i in result:
          Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
     Answer += "[end]"
     return Answer

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
     data = ""
     curr_date_time = datetime.datetime.now()
     day = curr_date_time.strftime("%A")
     date = curr_date_time.strftime("%d")
     month = curr_date_time.strftime("%B")
     year = curr_date_time.strftime("%Y")
     hour = curr_date_time.strftime("%H")
     minute = curr_date_time.strftime("%M")
     second = curr_date_time.strftime("%S")
     data += f"Use This real-time information if needed:\n"
     data += f"Day : {day}\n"
     data += f"Data: {date}\n"
     data += f"Month: {month}\n"
     data += f"Year: {year}\n"
     data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
     return data

def RealtimeSearchEngine(prompt):
     global SystemChatBot, messages

     with open(r"Data\ChatLog.json", "r") as f:
        content = f.read().strip()
        if content:
            messages = json.loads(content)
        else:
            messages = [] 
     messages.append({"role" : "user", "content" : f"{prompt}"})

     SystemChatBot.append({"role" : "system", "content": GoogleSearch(prompt)})

     completion = client.chat.completions.create(
          model="llama3-70b-8192",
          messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
          temperature=0.7,
          max_tokens=2048,
          top_p=1,
          stream=False,
          stop=None
     )

     Answer = ""

     if completion.choices and len(completion.choices) > 0:
          Answer = completion.choices[0].message.content
     else:
          Answer = "Sorry, I couldn't generate a response."
     
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
     SystemChatBot.pop()
     return AnswerModifier(Answer=Answer)


if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question >>>> ")
        if user_input.lower() in ["exit", "quit", "close"]:
            print("Exiting the chatbot...")
            break
        print(RealtimeSearchEngine(user_input))
  
