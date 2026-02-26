import io
import torch
import librosa
import numpy as np
import soundfile as sf

from .model import Generator
from . import config

# ==========================================
# 1. GLOBAL MODEL INITIALIZATION
# This runs only once when the server starts
# ==========================================
print(f"🎸 Initializing Jazz Generator on {config.DEVICE}...")

gen_j = Generator().to(config.DEVICE)
# Updated path to look inside the weights folder
checkpoint = torch.load("model/gen_j.pth.tar", map_location=config.DEVICE, weights_only=False)
gen_j.load_state_dict(checkpoint["state_dict"])
gen_j.eval() 

# ==========================================
# 2. PROCESSING FUNCTIONS
# ==========================================
def audio_to_chunks(audio_bytes):
    """
    Reads raw audio bytes from memory and returns a tensor of shape (N, 1, 128, 256)
    """
    # Read bytes from memory instead of a hard drive path
    y, sr = sf.read(io.BytesIO(audio_bytes))
    
    # Ensure audio is mono (soundfile reads stereo as 2D arrays)
    if len(y.shape) > 1:
        y = np.mean(y, axis=1)
        
    # Resample to 22050 if the uploaded file is at a different sample rate
    if sr != 22050:
        y = librosa.resample(y, orig_sr=sr, target_sr=22050)
        sr = 22050

    mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
    mel_spectrogram_db = librosa.power_to_db(mel_spectrogram, ref=np.max)

    # Normalize the data (-1 to 1)
    mel_spectrogram_db = np.clip((mel_spectrogram_db + 80) / 80.0 * 2 - 1, -1, 1)

    # Window slicing 
    num_sam = mel_spectrogram_db.shape[1]
    wind_size = 256
    ovrlap = 128

    data = []
    for i in range(0, num_sam - wind_size, ovrlap):
        data.append(mel_spectrogram_db[:, i : i + wind_size])
    
    data = np.array(data)
    data = np.expand_dims(data, axis=1)
    
    return data

def spec_to_sound(mel, sr=22050):
    """Reverses the spectrogram back to audio using Griffin-Lim."""
    mel = (mel + 1) / 2 * 80 - 80
    mel_power = librosa.db_to_power(mel)
    return librosa.feature.inverse.mel_to_audio(mel_power, sr=sr)

# ==========================================
# 3. MAIN API PIPELINE
# ==========================================
def process_pop_to_jazz(audio_bytes):
    """
    Takes raw audio bytes, processes them through the global CycleGAN model,
    and returns a memory buffer containing the new .wav file.
    """
    print("🎵 Preprocessing in-memory audio...")
    chunks = audio_to_chunks(audio_bytes) 
    chunks_tensor = torch.tensor(chunks, dtype=torch.float32).to(config.DEVICE)
    N = chunks_tensor.shape[0]
    
    print(f"🎷 Converting {N} chunks to Jazz style...")
    jazzy_chunks = []
    
    with torch.no_grad():
        with torch.amp.autocast(device_type=config.DEVICE):
            for i in range(N):
                chunk = chunks_tensor[i].unsqueeze(0) 
                # Uses the globally loaded gen_j
                fake_jazz = gen_j(chunk)
                jazzy_chunks.append(fake_jazz.to(torch.float32).squeeze().cpu().numpy())
                
    print("🪡 Stitching spectrograms together...")
    output_spec = []
    
    for i in range(N - 1):
        output_spec.append(jazzy_chunks[i][:, :128])
    output_spec.append(jazzy_chunks[-1])
    
    final_spec = np.concatenate(output_spec, axis=1)
    
    print("🔊 Synthesizing audio from spectrogram...")
    audio_array = spec_to_sound(final_spec, sr=22050)
    
    return audio_array