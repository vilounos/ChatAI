import discord
from discord.ext import commands

class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.help_message = ""
        self.text_channel_list = []
        self.set_message()

    def set_message(self):
        self.help_message = f"""
```
General commands:
{self.bot.command_prefix}help - Displays all the commands
{self.bot.command_prefix}q - Shows queue
{self.bot.command_prefix}p <keywords> - Plays a selected song from youtube + Resumes the song
{self.bot.command_prefix}skip - Skips the song
{self.bot.command_prefix}clear - Clears queue and leaves
{self.bot.command_prefix}stop - Bot leaves from VC
{self.bot.command_prefix}pause - Pauses the song
{self.bot.command_prefix}resume - Resumes playing
{self.bot.command_prefix}remove - Removes last queued song
```
"""

    @commands.command(name="help", help="Displays all the commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)
    @commands.command(name="model", help="Changes AI model (vilounos only)")
    async def model(self, ctx, *args):
        global charName
        allowed_user_id = 840187067887124480
                
        if ctx.author.id == allowed_user_id:
            charName = args[0]
            await self.bot.change_presence(activity=discord.Game(name=f"as {charName}"))
            ctx.send(f"Model changed to '{charName}' by vilounos")
            print(f"MODEL CHANGED: '{charName}'   by vilounos")
        else:
            ctx.send(f"Only vilounos can change AI model")