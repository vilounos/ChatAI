import openai
import os
import discord
import winsound
import sys
import pytchat
import time
import re
import pyaudio
import keyboard
import wave
import threading
import asyncio
import json
import socket
import pyttsx3
import logging
import webbrowser
import nest_asyncio
from utils.help_cog import help_cog
from utils.music_cog import music_cog
from discord.ext import commands
from datetime import timedelta
from threading import Timer
from emoji import demojize
from config import *
from utils.translate import *
from utils.TTS import *
from utils.promptMaker import *
from utils.subtitle import *
from utils.twitch_config import *
from termcolor import colored
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.app_context().push()
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
log.disabled = True

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

# https://openai.com/   config.py
openai.api_key = api_key

# Local AI
# openai.api_base = "http://localhost:1234/v1"

nest_asyncio.apply()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='ai.', intents=intents)
bot.remove_command('help')

charName = ""
    
last_dis_response_time = 0
serverid = "main"
mode = 0
total_characters = 0
chat = ""
chat_now = ""
chat_text = ""
chat_prev = ""
charLang = 0
dis_answer = ""
is_Speaking = False
console_output = []
owner_name = "vilounos"
history = []
blacklist = ["Nightbot"]
filters1 = ["i can't assist with that","i can't help with that","i can't help", "i can't assist", "i can't assist you"]
filters2 = ["filterThisWord"]


def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "input.wav"
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    print(colored("Speaking...", 'light_red'))
    while keyboard.is_pressed('RIGHT_SHIFT'):
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    transcribe_audio("input.wav")



@commands.command(name="model", help="Changes AI model (vilounos only)")
async def model(self, ctx, *args):
    global charName
    allowed_user_id = 840187067887124480
            
    if ctx.author.id == allowed_user_id:
        charName = args
        await bot.change_presence(activity=discord.Game(name=f"as {charName}"))
        ctx.send(f"Model changed to '{charName}' by vilounos")
        print(colored(f"MODEL CHANGED: '{charName}'   by vilounos",'red'))
    else:
        ctx.send(f"Only vilounos can change AI model")

def transcribe_audio(file):
    global chat_now
    try:
        audio_file= open(file, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        chat_now = transcript.text
        console_output.append("You: " + chat_now)
        print ("You: " + chat_now)
    except Exception as e:
        print(colored("Error transcribing audio: {0}".format(e), 'red'))
        return

    result = owner_name + " said " + chat_now
    conversation.append({'role': 'user', 'content': result})
    openai_answer()
    
def chat_by_text():
    global chat_now
    global chat_text
    chat_now = chat_text
    chat_text = ""
    print ("Text: " + chat_now)

    result = owner_name + " said " + chat_now
    conversation.append({'role': 'user', 'content': result})
    openai_answer()

def openai_answer():
    global total_characters, conversation, charName, mode, serverid, history, dis_answer

    if mode == 4:
        directory = f"characterConfig/{charName}/{serverid}"
        os.makedirs(directory, exist_ok=True)
        
    elif mode == 5:
        directory = f"characterConfig/{charName}"
        os.makedirs(directory, exist_ok=True)
    
    total_characters = sum(len(d['content']) for d in conversation)

    while total_characters > 5000000:
        try:
            conversation.pop(2)
            total_characters = sum(len(d['content']) for d in conversation)
        except Exception as e:
            print(colored("Error removing old messages: {0}".format(e), 'red'))
    if mode == 4:
        try:
            with open("characterConfig/" + charName + "/" + serverid + "/conversation.json", "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            print(colored("History loading error", 'red'))
            
    if mode == 5:
        try:
            with open("characterConfig/" + charName + "/conversation.json", "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            print(colored("History loading error", 'red'))
    if mode == 4:
        with open("characterConfig/" + charName + "/" + serverid + "/conversation.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
    else:
        with open("characterConfig/" + charName + "/conversation.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
    if mode == 4:
        prompt = getPrompt(charName, mode, serverid)
    else:
        prompt = getPrompt(charName, mode, "main")

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=prompt,
        max_tokens=1024,
        temperature=1,
        top_p=1 
    )
    message = response['choices'][0]['message']['content']
    if mode != 4 and mode != 5:
        conversation.append({'role': 'assistant', 'content': message})


    lowerMessage = message.lower()
    for word in filters1 :
        if word in lowerMessage:
            console_output.append('Filter: ' + message)
            print(colored('Filter: ' + message, 'light_blue'))
            print(colored('Word: ' + word, 'light_blue'))
            message = 'Filtered!'
            break

    for word in filters2 :
        if word in lowerMessage:
            console_output.append('Filter: ' + message)
            print(colored('Filter: ' + message, 'light_blue'))
            print(colored('Word: ' + word, 'light_blue'))
            message = 'Filtered!'
            break

    if mode == 4:
        dis_answer = message
        print(colored("AI: " + dis_answer, 'green'))
    elif mode == 5:
        dis_answer = message
        print(colored("AI: " + dis_answer, 'green'))
    else:
        translate_text(message)

def yt_livechat(video_id):
        global chat

        live = pytchat.create(video_id=video_id)
        while live.is_alive():
            try:
                for c in live.get().sync_items():
                    if c.author.name in blacklist:
                        continue
                    if not c.message.startswith("!"):
                        chat_raw = re.sub(r':[^\s]+:', '', c.message)
                        chat_raw = chat_raw.replace('#', '')
                        chat = c.author.name + ': ' + chat_raw
                        print(colored(chat, 'blue'))
                        
                    time.sleep(1)
            except Exception as e:
                print(colored("Error receiving chat: {0}".format(e), 'red'))

def twitch_livechat():
    global chat
    sock = socket.socket()

    sock.connect((server, port))

    sock.send(f"PASS oauth:{token}\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\n".encode('utf-8'))

    regex = r":(\w+)!\w+@\w+\.tmi\.twitch\.tv PRIVMSG #\w+ :(.+)"

    while True:
        try:
            resp = sock.recv(2048).decode('utf-8')

            if resp.startswith('PING'):
                    sock.send("PONG\n".encode('utf-8'))
                    
            else:
                resp = demojize(resp)
                match = re.match(regex, resp)

                username = match.group(1)
                message = match.group(2)

                if username in blacklist:
                    continue
                
                chat = username + ': ' + message
                
                console_output.append(chat)
                print(colored(chat, 'blue'))
                return redirect(url_for('main_web'))

        except Exception as e:
            print(colored("Error: {0}".format(e), 'red'))

def translate_text(text):
    global is_Speaking

    detect = detect_google(text)
    if charLang == 1:
        tts = translate_google(text, f"{detect}", "EN")
    elif charLang == 2:
        tts = translate_google(text, f"{detect}", "JA")
        tts_en = translate_google(text, f"{detect}", "EN")
        print(colored("EN: " + tts_en, 'blue'))
    else:
        tts = translate_google(text, f"{detect}", "EN")
    
    console_output.append("AI: " + tts)
    print(colored("AI: " + tts, 'green'))
    
    generate_subtitle(chat_now, text)


    if charLang == 1:
        fast_tts(tts)
    elif charLang == 2:
        voicevox_tts(tts)


    time.sleep(1)

    if charLang == 2:
        is_Speaking = True
        winsound.PlaySound("test.wav", winsound.SND_FILENAME)
        is_Speaking = False

    time.sleep(1.5)
    
    with open ("output.txt", "w") as f:
        f.truncate(0)
    with open ("chat.txt", "w") as f:
        f.truncate(0)
        
def translate_dis(text):
    
    global is_Speaking, dis_answer

    
    detect = detect_google(text)
    if charLang == 1:
        tts = translate_google(text, f"{detect}", "EN")
    elif charLang == 2:
        tts = translate_google(text, f"{detect}", "JA")
        tts_en = translate_google(text, f"{detect}", "EN")
        print(colored("EN: " + tts_en, 'blue'))
    else:
        tts = translate_google(text, f"{detect}", "EN")
    
    console_output.append("AI: " + text)
    print(colored("AI: " + text, 'green'))
    
    
    dis_answer = text
    

    with open ("output.txt", "w") as f:
        f.truncate(0)
    with open ("chat.txt", "w") as f:
        f.truncate(0)

def preparation():
    global conversation, chat_now, chat, chat_prev
    while True:
        chat_now = chat
        if is_Speaking == False and chat_now != chat_prev:
            conversation.append({'role': 'user', 'content': chat_now})
            chat_prev = chat_now
            openai_answer()
        time.sleep(1)

@app.route('/start', methods=['POST'])
def start():
    global mode, charLang, charName, console_output, conversation, history
    if 'mode' in request.form:
        mode = int(request.form['mode'])
    if 'charLang' in request.form:
        charLang = int(request.form['charLang'])
    if 'charName' in request.form:
        charName = request.form['charName']
    if mode == 4:
        directory = f"characterConfig/{charName}/main"
        os.makedirs(directory, exist_ok=True)
        try:
            conversation = []
            history = []
            with open("characterConfig/" + charName + "/main" + "/conversation.json", "r", encoding="utf-8") as f:
                history = json.load(f)
                conversation = history.get("history", [])
        except (FileNotFoundError, json.JSONDecodeError):
            conversation = []
    if mode == 5:
        directory = f"characterConfig/{charName}"
        os.makedirs(directory, exist_ok=True)
        try:
            conversation = []
            history = []
            with open("characterConfig/" + charName + "/conversation.json", "r", encoding="utf-8") as f:
                history = json.load(f)
                conversation = history.get("history", [])
        except (FileNotFoundError, json.JSONDecodeError):
            conversation = []
    else:
        try:
            conversation = []
            history = []
            with open("characterConfig/" + charName + "/conversation.json", "r", encoding="utf-8") as f:
                history = json.load(f)
                conversation = history.get("history", [])
        except (FileNotFoundError, json.JSONDecodeError):
            conversation = []
    history = {"history": conversation}
  
    console_output.append(f"AI Started... Mode: {mode} | TTS: {charLang} | Name: {charName}")
    print(colored(f"AI Started... Mode: {mode} | TTS: {charLang} | Name: {charName}", 'green'))


    if mode == 1:
        threading.Thread(target=record_mode).start()
    elif mode == 2:
        live_id = request.form.get("live_id", "")
        threading.Thread(target=yt_livechat, args=(live_id,)).start()
    elif mode == 3:
        threading.Thread(target=preparation).start()
        threading.Thread(target=twitch_livechat).start()
    elif mode == 4:
        thread = threading.Thread(target=run_async_in_thread, args=(discord_chat(),))
        thread.start()
        thread.join()
    elif mode == 5:
        thread = threading.Thread(target=run_async_in_thread, args=(discord_chat(),))
        thread.start()
        thread.join()

    return redirect(url_for('main_web'))
    
    
def run_async_in_thread(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task = loop.create_task(coro)
    try:
        loop.run_until_complete(task)
    finally:
        loop.close()

def record_mode():
    print(colored("Hold R Shift to speak", 'green'))
    while True:
        if chat_text != "":
            chat_by_text()
        elif keyboard.is_pressed('RIGHT_SHIFT'):
            record_audio()

@app.route('/')
def index():
    return render_template('index.html', mode=mode, charLang=charLang, charName=charName)


@app.route('/main')
def main_web():
    return render_template('main.html', console_output=console_output)

@app.route('/stop', methods=['POST'])
def stop():
    global console_output
    console_output.append("!!STOPPING!!")
    print(colored("!!STOPPING!!", 'red'))
    os._exit(0)
    sys.exit()
    exit()
    quit()
    return redirect(url_for('index'))

@app.route('/command', methods=['POST'])
def command():
    global console_output
    global chat_text
    command = request.form['command']
    
    if command.lower().startswith('/say '):
        text = command[5:]
        forcesay(text)
    elif command.lower().startswith('/chat '):
        chat_text = command[6:]
        console_output.append(f"Chat: {chat_text}")
    else:
        console_output.append(f"Unknown command: {command}")
        print(colored(f"Unknown command: {command}", 'red'))
    
    return redirect(url_for('main_web'))
    
def forcesay(text):
    global is_Speaking
    global console_output
    console_output.append(f"Say: {text}")
    print(colored(f"Say: {text}", 'yellow'))

    console_output.append("AI: " + text)
    print(colored("AI: " + text, 'cyan'))
    
    
    if charLang == 1:
        fast_tts(text)
    elif charLang == 2:
        voicevox_tts(text)

    generate_subtitle("", text)

    time.sleep(1)

    is_Speaking = True
    if charLang == 2:
        winsound.PlaySound("test.wav", winsound.SND_FILENAME)
    is_Speaking = False

    time.sleep(1)
    with open ("output.txt", "w") as f:
        f.truncate(0)
    with open ("chat.txt", "w") as f:
        f.truncate(0)



async def send_long_message(message, text, max_length=2000):
    while len(text) > max_length:
        split_index = text.rfind(' ', 0, max_length)
        if split_index == -1:
            split_index = max_length 
        await message.reply(text[:split_index])
        text = text[split_index:].lstrip()

    if text:
        await message.reply(text)
    


async def discord_chat():
    async with bot:
        await bot.add_cog(help_cog(bot))
        await bot.add_cog(music_cog(bot))
        await bot.run(DISTOKEN)


@bot.event
async def on_ready():
    global charName
    print(colored(f'Login as {bot.user}', 'green'))
    await bot.change_presence(activity=discord.Game(name=f"as {charName}"))

@bot.event
async def on_message(message): 
    global conversation, chat_now, last_dis_response_time, dis_white_id, serverid, dis_black_id, charName
    
    if message.author == bot.user:
        return
    
    if message.guild and mode != 5:
        serverid = str(message.guild.id)
        directory = f"characterConfig/{charName}/{serverid}"
        os.makedirs(directory, exist_ok=True)
        try:
            with open(f"characterConfig/{charName}/{serverid}/conversation.json", "r", encoding="utf-8") as f:
                history = json.load(f)
                conversation = history.get("history", [])
        except:
            print(colored("History loading error", 'red'))
            conversation = []
            
        bot_mention = f'<@{bot.user.id}>'
        question = message.content.replace(bot_mention, '').strip()
        
        for mention in message.mentions:
            mention_str = f'<@{mention.id}>'
            question = question.replace(mention_str, mention.display_name)
            
        for channel in message.channel_mentions:
            channel_mention_str = f'<#{channel.id}>'
            question = question.replace(channel_mention_str, channel.name)
        
        nickname = message.author.display_name
        channel_name = message.channel.name
        author = message.author
        permissions = message.channel.permissions_for(message.author)
        
        if permissions.administrator:
            chat_now = f"{time.ctime()} {nickname} (administrator) in channel {channel_name}: {question}"
        else:
            chat_now = f"{time.ctime()} {nickname} in channel {channel_name}: {question}"
        
        print(colored(f"Chat Now: {chat_now}", 'blue'))

        if any(mention.id == bot.user.id for mention in message.mentions):
            current_time = time.time()
            UpdateListsID()
            if not str(message.author.id) in dis_black_id:
                if str(message.author.id) in dis_white_id:
                    print(colored(f"User on whitelist: {nickname}  ({message.author.id})", 'light_grey'))
                else:
                    print(colored(f"Author UID: {message.author.id}", 'light_grey'))
                    last_dis_response_time = current_time
                
                if charName.lower() == "storymaking":
                    conversation.append({'role': 'system', 'content': "You create longer parts. At least 5 sentences per part. Use maximum of 3000 characters per whole message. You give user to decide between at least 5 decisions."})
                conversation.append({'role': 'user', 'content': chat_now})
                with open(f"characterConfig/{charName}/{serverid}/conversation.json", "w", encoding="utf-8") as f:
                    json.dump({"history": conversation}, f, indent=4)
                        
                openai_answer()
                dis_answer_with_mentions = replace_nicknames_with_mentions(dis_answer, message.guild)
                time.sleep(1)
                    
                if False: #dis_answer_with_mentions.lower().startswith("timeout"):
                    if not permissions.administrator:
                        if not str(message.author.id) in dis_white_id:
                            try:
                                await author.timeout(timedelta(minutes=1), reason="Banned by Samantha for nudity")
                                dis_answer_with_mentions = f"User {author.mention} has been timed out for 1 minute because of nudity (:"
                                print(colored(f"User {author.mention} has been timed out for 1 minute because of nudity (:", 'yellow'))
                            except discord.Forbidden:
                                dis_answer_with_mentions = f"Why I can't timeout you :("
                                print(colored("No Permissions for timeout!", 'red'))
                            except Exception as e:
                                dis_answer_with_mentions = f"Why I can't timeout you :("
                                print(colored("Can't timeout: {0}".format(e), 'red'))

                            conversation.append({'role': 'assistant', 'content': dis_answer_with_mentions})
                                    
                            with open(f"characterConfig/{charName}/{serverid}/conversation.json", "w", encoding="utf-8") as f:
                                json.dump({"history": conversation}, f, indent=4)
                        else:
                            print(colored(f"User is on whitelist... No timeout: {nickname}  ({message.author.id})", 'yellow'))
                    else:
                        print(colored(f"User is an administrator... No timeout: {nickname}  ({message.author.id})", 'yellow')) 
                else:
                    conversation.append({'role': 'assistant', 'content': dis_answer_with_mentions})
                        
                    with open(f"characterConfig/{charName}/{serverid}/conversation.json", "w", encoding="utf-8") as f:
                        json.dump({"history": conversation}, f, indent=4)
            else:
                conversation.append({'role': 'user', 'content': chat_now})
                with open(f"characterConfig/{charName}/{serverid}/conversation.json", "w", encoding="utf-8") as f:
                    json.dump({"history": conversation}, f, indent=4)
                dis_answer_with_mentions = "You are blacklisted :( Ask **vilounos** to remove you from blacklist!"
                conversation.append({'role': 'assistant', 'content': dis_answer_with_mentions})
                
                with open(f"characterConfig/{charName}/{serverid}/conversation.json", "w", encoding="utf-8") as f:
                    json.dump({"history": conversation}, f, indent=4)
            await send_long_message(message, dis_answer_with_mentions)
            
        # Save all messages
        else:
            conversation.append({'role': 'user', 'content': chat_now})
           
            with open(f"characterConfig/{charName}/{serverid}/conversation.json", "w", encoding="utf-8") as f:
                json.dump({"history": conversation}, f, indent=4)
        
    # else:
        # Self learning code
        # author = message.author
        # if str(message.author.id) == "840187067887124480":
            # directory = f"characterConfig/{charName}"
            # os.makedirs(directory, exist_ok=True)
            # try:
                # with open(f"characterConfig/{charName}/conversation.json", "r", encoding="utf-8") as f:
                    # history = json.load(f)
                    # conversation = history.get("history", [])
            # except:
                # print(colored("History loading error", 'red'))
                # conversation = []
                
            # question = message.content
            
            # for mention in message.mentions:
                # mention_str = f'<@{mention.id}>'
                # question = question.replace(mention_str, mention.display_name)
            
            # nickname = message.author.display_name
            
            # chat_now = f"{question}"
            
            # print(colored(f"Chat Now: {chat_now}", 'blue'))

            # current_time = time.time()
        
            # conversation.append({'role': 'user', 'content': chat_now})
            # with open(f"characterConfig/{charName}/conversation.json", "w", encoding="utf-8") as f:
                # json.dump({"history": conversation}, f, indent=4)
                
            # openai_answer()
            # time.sleep(1)
            # conversation.append({'role': 'assistant', 'content': dis_answer})
            # with open(f"characterConfig/{charName}/conversation.json", "w", encoding="utf-8") as f:
                # json.dump({"history": conversation}, f, indent=4)

            # await message.reply(dis_answer)
        
        
        
    await bot.process_commands(message)

def UpdateListsID():
    global dis_white_id, dis_black_id, filters2
    blacklist = "discfg/blacklist.txt"
    whitelist = "discfg/whitelist.txt"
    filters2list = "discfg/filters.txt"
    try:
        with open(whitelist, 'r', encoding='utf-8') as file:
            dis_white_id = [line.strip() for line in file]
    except:
        print(colored("Failed to load whitelist!",'red'))
    try:
        with open(blacklist, 'r', encoding='utf-8') as file:
            dis_black_id = [line.strip() for line in file]
    except:
        print(colored("Failed to load blacklist!",'red'))
    try:
        with open(filters2list, 'r', encoding='utf-8') as file:
            filters2 = [line.strip() for line in file]
    except:
        print(colored("Failed to load filters!",'red'))

    print(colored("IDs updated!",'red'))

    
def replace_nicknames_with_mentions(response, guild):
    for member in guild.members:
        placeholder = f"@{member.display_name}"
        mention = f"<@{member.id}>"
        response = response.replace(placeholder, mention)
    return response
    
    
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')
        
if __name__ == '__main__':
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        Timer(1, open_browser).start()
    with app.app_context():
        app.run(debug=True)
        