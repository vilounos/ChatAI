import discord

TOKEN = 'MTI3MDAyNDE1MDMxNjIyNDYyMg.GPbkw5.Gr6Guv0jmmQkEbJr2OaL0N9YeH4raWgmSdQP4Y'

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f'Přihlášen jako {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        response = message.content.replace(f'<@{client.user.id}>', '').strip()
        await message.channel.send(response)

# Spuštění bota
client.run(TOKEN)