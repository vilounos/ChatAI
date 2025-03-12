import os
import torch
import requests
import sounddevice as sd
import numpy as np
import pyttsx3
import urllib.parse
from termcolor import colored
#from utils.katakana import *


def silero_tts(tts, language, model, speaker, chunk_size=50):
    device = torch.device('cpu')
    torch.set_num_threads(4)
    local_file = 'model.pt'

    if not os.path.isfile(local_file):
        torch.hub.download_url_to_file(f'https://models.silero.ai/models/tts/{language}/{model}.pt',
                                    local_file)  

    model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
    model.to(device)

    sample_rate = 48000

    words = tts.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

    for chunk in chunks:
        audio = model.apply_tts(text=chunk, speaker=speaker, sample_rate=sample_rate)
        
        audio = np.array(audio, dtype=np.float32)
        
        sd.play(audio, samplerate=sample_rate)
        sd.wait()
    
def voicevox_tts(tts):
    # Run Voicevox first
    
    voicevox_url = 'http://localhost:50021'
    katakana_text = katakana_converter(tts)
    # https://voicevox.hiroshiba.jp
    params_encoded = urllib.parse.urlencode({'text': katakana_text, 'speaker': 14})
    request = requests.post(f'{voicevox_url}/audio_query?{params_encoded}')
    params_encoded = urllib.parse.urlencode({'speaker': 14, 'enable_interrogative_upspeak': True})
    request = requests.post(f'{voicevox_url}/synthesis?{params_encoded}', json=request.json())

    with open("test.wav", "wb") as outfile:
        outfile.write(request.content)
        
        
def fast_tts(text):
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')

    engine.setProperty('voice', voices[0].id)

    engine.setProperty('rate', 130)

    engine.setProperty('volume', 0.9)

    engine.say(text)

    engine.runAndWait()


if __name__ == "__main__":
    fast_tts("Hello, How are you doing? I am pretty well! What about you?")
