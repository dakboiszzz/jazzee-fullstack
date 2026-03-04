import io
import torch
import soundfile as sf
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

import os
import yt_dlp
from pydantic import BaseModel

class YouTubeRequest(BaseModel):
    url: str

from model.sample import process_pop_to_jazz
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jazzee-fullstack.vercel.app"], # In production, you change this to your actual React website URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def download_youtube_audio(url: str) -> bytes:
    # 1. Configure yt-dlp to download only audio and convert to WAV
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': 'temp_youtube_audio.%(ext)s', # Save to this temporary filename
        'quiet': True 
    }
    
    # 2. Execute the download
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
    # 3. Read the downloaded file into bytes (this perfectly mimics your old 'await file.read()')
    with open('temp_youtube_audio.wav', 'rb') as f:
        audio_bytes = f.read()
        
    # 4. Clean up your hard drive by deleting the temp file
    if os.path.exists('temp_youtube_audio.wav'):
        os.remove('temp_youtube_audio.wav')
        
    return audio_bytes

@app.get('/')
def index():
    return {"message" : "Hello World!"}

@app.post('/jazz')
def convert_pop_to_jazz(request: YouTubeRequest):
    song = download_youtube_audio(request.url)
    
    output = process_pop_to_jazz(song)
    audio_numpy = output.squeeze()
    # DEBUG: This will print in your terminal so we know the model actually made sound!
    print(f"Generated audio shape: {audio_numpy.shape}")

    # 2. Create an empty virtual file in your computer's memory
    memory_file = io.BytesIO()

    # 3. Write the audio math into the file and FORCE 16-bit PCM format!
    sf.write(memory_file, audio_numpy, samplerate=24000, format='WAV', subtype='PCM_16')

    # 4. Extract the fully packaged bytes
    audio_bytes = memory_file.getvalue()

    # 5. Return a solid Response and manually declare the file size to stop chunking
    return Response(
        content=audio_bytes, 
        media_type="audio/wav",
        headers={
            "Content-Length": str(len(audio_bytes)),
            "Content-Disposition": 'inline; filename="jazz.wav"' 
        }
    )
