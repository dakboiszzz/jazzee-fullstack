from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse

from model.sample import process_pop_to_jazz
app = FastAPI()

@app.get('/')
def index():
    return {"message" : "Hello World!"}

@app.post('/jazz')
async def convert_pop_to_jazz(file: UploadFile = File(...)):
    song = await file.read()
    output = process_pop_to_jazz(song)
    return StreamingResponse(
        output, 
        media_type="audio/wav",
    )
