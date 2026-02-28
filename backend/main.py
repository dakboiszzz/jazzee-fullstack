import io
import torch
import soundfile as sf
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from model.sample import process_pop_to_jazz
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you change this to your actual React website URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def index():
    return {"message" : "Hello World!"}

@app.post('/jazz')
async def convert_pop_to_jazz(file: UploadFile = File(...)):
    song = await file.read()
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
