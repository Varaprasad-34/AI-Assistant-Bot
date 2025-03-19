from AppOpener import close, open as appopen
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

#Define CSS classes for parsing specific elements in HTML content.
classes = ["zCubwf", "hgKElc", "LTKOO SY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee"
"tw-Data-text tw-text-small tw-ta",
"IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table",
"dDoNo ikb4Bb gsrt", "sXLa0e","LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

User_Agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

professional_reaponse = [
     "Your satisfaction os my top priority; feel free to reach out if there's anything else I can help you."
     "I'm at your service for any additional qestions or support you may need-don't hesistate to ask."
]

messages = []

SystemChatBot = [{"role": "System", "content" : f"Hello, I am {os.environ['Username']}, You're content writer. You have to write content"}]


def googleSearch(Topic):
     search(Topic)
     return True

def Content(Topic):
     def OpenNotepad(File):
          default_text_editor = 'notepad.exe'
          subprocess.Popen([default_text_editor, File])

     def ContentWriterAI(Prompt):
          messages.append({"role": "user", "content": f"{Prompt}"})

          try:
               completion = client.chat.completions.create(
               model="mixtral-8x7b-32768",  # Corrected model name
               messages=messages,  # Use the updated messages array
               max_tokens=2048,
               temperature=0.7,
               top_p=1,
               stream=False,  # Disable streaming for simplicity
               stop=None
               )

               # Extract the response content
               if completion.choices and len(completion.choices) > 0:
                    Answer = completion.choices[0].message.content
               else:
                    Answer = "Sorry, I couldn't generate a response."
               Answer = Answer.replace("</s>", "")  # Clean up the output
               messages.append({"role": "assistant", "content": Answer}) 
               return Answer

          except Exception as e:
               print(f"Error in ContentWriterAI: {e}")
               return "An error occurred while generating the response."

     Topic = Topic.replace("Content ", "")
     ContentByAi = ContentWriterAI(Topic)

    # Save the content to a file
     file_path = os.path.join("Data/AiContent", f"{Topic.lower().replace(' ', '')}.txt")
     try:
          with open(file_path, "w", encoding="utf-8") as file:
               file.write(ContentByAi)
          OpenNotepad(file_path)
          return True
     except Exception as e:
          print(f"Error saving file: {e}")
          return False
Content("eassay on node js")
def YouTubeSearch(Topic):
     Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
     webbrowser.open(Url4Search)
     return True

def PlayYoutube(query):
     playonyt(query)
     return True

def OpenApp(app, sess=requests.Session()):
     try:
          appopen(app, match_closest=True, output=True, throw_error=True)
          return True
     except:

          def extract_link(html):
               if html is None:
                    return []
               soup = BeautifulSoup(html, 'html.parser')
               links = soup.find("a", {"jsname": 'UWckNb'})
               return [link.get("href") for link in links]
          
          def search_google(query):
               url = f"https://www.google.com/search?q={query}"
               header = {"User-Agent": User_Agent}
               response = sess.get(url, headers=header)

               if response.status_code == 200:
                    return response.text
               else:
                    print("Failed to retrive search results.")
                    return None
          
          html = search_google(app)
           
          if html:
               link = extract_link(html)[0]
               webopen(link)
          
          return True
def CloseApp(app):

     if "chrome" in app:
          pass
     else:
          try:
               close(app, match_closest=True, output=True, throw_error=True)
               return True
          except:
               return False

def System(command):

     def mute():
          keyboard.press_and_release("volume mute")

     def unmute():
          keyboard.press_and_release("volume mute")

     def volume_up():
          keyboard.press_and_release("volume up")
     
     def volume_down():
          keyboard.press_and_release("volume down")
     
     if command == "mute":
          mute()
     elif command == "unmute":
          unmute()
     elif command == "volume_up":
          volume_up()
     elif command == "volume_down":
          volume_down()

     return True

async def TranslateAdndExecute(commands: list[str]):

     funcs = []

     for command in commands:
          if command.startswith("open "):
               if "open if" in command or "open file" == command:
                    continue
               else: 
                    funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))

          elif command.startswith("close "):
               funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))

          elif command.startswith("play "):
               funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))

          elif command.startswith("content "):
               funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))

          elif command.startswith("youtube search "):
               funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))

          elif command.startswith("system "):
               funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))

          else:
               print(f"No function found for: {command}")


     results = await asyncio.gather(*funcs)
     for result in results:
        yield result

async def Automation(commands: list[str]):

     async for result in TranslateAdndExecute(commands):
          pass
     return True
