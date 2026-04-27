import asyncio
import edge_tts
import os
import requests
from bs4 import BeautifulSoup
import subprocess

url = 'https://habr.com/ru/companies/avito/articles/1026786/'
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

content = soup.find('div', id='post-content-body')

text = ""
if content:
    for tag in content.find_all(['figure', 'script', 'style']):
        tag.decompose()
    text = content.get_text(separator='\n', strip=True)

def split_text(text, max_length=3000):
    chunks = []
    while text:
        chunk = text[:max_length]
        last_dot = chunk.rfind('.')
        if last_dot != -1:
            chunk = chunk[:last_dot+1]
        chunks.append(chunk)
        text = text[len(chunk):]
    return chunks

async def generate_audio():
    os.makedirs("./result", exist_ok=True)
    chunks = split_text(text)

    for i, chunk in enumerate(chunks):
        communicate = edge_tts.Communicate(
            text=chunk,
            voice="ru-RU-DmitryNeural"
        )
        await communicate.save(f"./result/part_{i}.mp3")

def merge_audio_ffmpeg():
    list_path = "./result/list.txt"

    with open(list_path, "w", encoding="utf-8") as f:
        i = 0
        while True:
            path = f"./result/part_{i}.mp3"
            if not os.path.exists(path):
                break
            f.write(f"file '{path}'\n")
            i += 1

    subprocess.run([
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        "./result/final.mp3"
    ])

asyncio.run(generate_audio())
merge_audio_ffmpeg()

os.startfile("./result/final.mp3")