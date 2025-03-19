import asyncio
import os
import requests
import aiohttp
from PIL import Image
from dotenv import get_key
from time import sleep

# Define API Constants
API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
HEADERS = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Folder to store images
IMAGE_FOLDER = "Data\AIimages"
os.makedirs(IMAGE_FOLDER, exist_ok=True)  # Ensure the folder exists


def open_image(prompt):
    """Open generated images for a given prompt."""
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = os.path.join(IMAGE_FOLDER, jpg_file)

        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")


async def generate_image(prompt: str):
    """Generate images asynchronously from the Hugging Face API."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(4):
            payload = {"inputs": f"{prompt}, ultra-detailed, 4K resolution, cinematic lighting"}
            task = asyncio.create_task(fetch_image(session, payload, prompt, i + 1))
            tasks.append(task)

        await asyncio.gather(*tasks)


async def fetch_image(session, payload, prompt, image_num):
    """Fetch image from API and save it."""
    try:
        async with session.post(API_URL, headers=HEADERS, json=payload) as response:
            if response.status == 200:
                image_bytes = await response.read()
                file_path = os.path.join(IMAGE_FOLDER, f"{prompt.replace(' ', '_')}{image_num}.jpg")
                with open(file_path, "wb") as f:
                    f.write(image_bytes)
                print(f"Saved: {file_path}")
            else:
                print(f"Failed to fetch image {image_num}: {response.status} - {await response.text()}")
    except Exception as e:
        print(f"Error fetching image {image_num}: {e}")


def GenerateImage(prompt: str):
    """Generate and open images."""
    asyncio.run(generate_image(prompt))
    open_image(prompt)


while True:
    try:
        file_path = r"Frontend\Files\ImageGeneration.data"

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = f.read().strip()

            if data:
                Prompt, Status = data.split(",")

                if Status == 'True':
                    print("Generating Image....")
                    GenerateImage(prompt=Prompt)

                    with open(file_path, "w") as f:
                        f.write("False,False")
                    break
        sleep(1)
    except:
        pass
