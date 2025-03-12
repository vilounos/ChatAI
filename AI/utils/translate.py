import requests
import json
import sys
import googletrans
from termcolor import colored

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

def translate_deeplx(text, source, target):
    url = "http://localhost:1188/translate"
    headers = {"Content-Type": "application/json"}

    params = {
        "text": text,
        "source_lang": source,
        "target_lang": target
    }

    payload = json.dumps(params)

    response = requests.post(url, headers=headers, data=payload)

    data = response.json()

    translated_text = data['data']

    return translated_text

def translate_google(text, source, target):
    try:
        translator = googletrans.Translator()
        result = translator.translate(text, src=source, dest=target)
        return result.text
    except:
        print("Error translate")
        return "Translation error"
    
def detect_google(text):
    try:
        translator = googletrans.Translator()
        result = translator.detect(text)
        return result.lang.upper()
    except:
        print("Error detect")
        return "EN"

if __name__ == "__main__":
    text = "Hello there"
    source = translate_deeplx(text, "ID", "EN")
    print(source)
