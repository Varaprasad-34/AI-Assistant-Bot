from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    SetMicrophoneStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDDM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

# Define functions
Functions = ["open", "close", "play", "content", "google search", "youtube search"]
subprocesses = []

def ShowDefaultChatIfNoChats():
    """Ensure the chat log is initialized if empty."""
    try:
        with open(r'Data\ChatLog.json', "r", encoding="utf-8") as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding="utf-8") as file:
                    file.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding="utf-8") as file:
                    file.write("")
    except FileNotFoundError:
        print("Error: ChatLog.json not found.")

def ReadChatLogJson():
    """Read and return the chat log data."""
    try:
        with open(r"Data\ChatLog.json", "r", encoding="utf8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: ChatLog.json not found.")
        return []

def ChatLogIntegration():
    """Format and integrate chat log data into the GUI."""
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")
    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    """Display chat data on the GUI."""
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
            data = file.read()
            if len(data) > 0:
                lines = data.split('\n')
                result = '\n'.join(lines)
                with open(TempDirectoryPath('Responses.data'), "w", encoding="utf-8") as file:
                    file.write(result)
    except FileNotFoundError:
        print("Error: Database.data not found.")

def InitialExecution():
    """Initialize the application."""
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    """Execute the main logic for processing user queries."""
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""
    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDDM(Query)
    
    print("")
    print(f"Decision: {Decision}")
    print("")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    Merged_query = " and ".join(
        ["".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if not TaskExecution and any(queries.startswith(func) for func in Functions):
            if any(queries.startswith(list(Decision))):
               run(Automation(list(Decision)))
               TaskExecution = True

    if ImageExecution:
        try:
            with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
                file.write(f"{ImageGenerationQuery}, True")
            p1 = subprocess.Popen(['python', r'Backend\ImageGeneration.py'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")
    if (G and R) or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True
    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general", "")
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = ChatBot(QueryModifier(QueryFinal))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                os._exit(1)

def FirstThread():
    """Handle the main execution loop in a separate thread."""
    while True:
        try:
            CurrentStatus = GetMicrophoneStatus()
            if CurrentStatus == "True":
                MainExecution()
            else:
                AIStatus = GetAssistantStatus()
                if "Available..." not in AIStatus:
                    SetAssistantStatus("Available...")
                sleep(0.1)
        except Exception as e:
            print(f"Error in FirstThread: {e}")

def SecondThread():
    """Start the GUI in a separate thread."""
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()