import json
import sys
from termcolor import colored

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

outputNum = 1000

def getIdentity(identityPath):  
    with open(identityPath, "r", encoding="utf-8") as f:
        identityContext = f.read()
    return {"role": "user", "content": identityContext}
    
def getPrompt(charName, mode, serverid):
    total_len = 0
    data = []
    prompt = []
    prompt.append(getIdentity("characterConfig/" + charName + "/identity.txt"))
    prompt.append({"role": "system", "content": f"Below is conversation history.\n"})

    if mode == 4:
        with open("characterConfig/" + charName + "/" + serverid + "/conversation.json", "r") as f:
            data = json.load(f)
    elif mode == 5:
        with open("characterConfig/" + charName + "/conversation.json", "r") as f:
            data = json.load(f)
    else:
        with open("characterConfig/" + charName + "/conversation.json", "r") as f:
            data = json.load(f)
    history = data["history"]
    for message in history[:-1]:
        prompt.append(message)

    prompt.append(
        {
            "role": "system",
            "content": f"Here is the latest conversation.\n*Make sure your response is within {outputNum} characters!\n",
        }
    )
    if history:
        print("History")
        prompt.append(history[-1])
    else:
        print("No history")

    total_len = sum(len(d['content']) for d in prompt)
    
    while total_len > 4000:
        try:
            prompt.pop(2)
            total_len = sum(len(d['content']) for d in prompt)
        except:
            print("Error: Prompt too long!")

    return prompt

if __name__ == "__main__":
    prompt = getPrompt("charName", "4", "main")
    print(prompt)
    print(len(prompt))