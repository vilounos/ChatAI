import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import asyncio

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music_data = {}
        self.YDL_OPTIONS = {'format': 'bestaudio/best'}
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)

    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return {'source': item, 'title': title}
            
            
        # Nefunkční vyhledávání pomocí Key Word(s)
        
        #search = VideosSearch(it em, limit=1)
        #return {'source': search.result()["result"][0]["link"], 'title': search.result()["result"][0]["title"]}
        
        
        

    async def play_next(self, ctx):
        server_id = ctx.guild.id
        if server_id in self.music_data and len(self.music_data[server_id]['queue']) > 0:
            self.music_data[server_id]['is_playing'] = True

            m_url = self.music_data[server_id]['queue'][0][0]['source']
            self.music_data[server_id]['queue'].pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.music_data[server_id]['vc'].play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
        else:
            self.music_data[server_id]['is_playing'] = False

    async def play_music(self, ctx):
        server_id = ctx.guild.id
        if server_id in self.music_data and len(self.music_data[server_id]['queue']) > 0:
            self.music_data[server_id]['is_playing'] = True

            m_url = self.music_data[server_id]['queue'][0][0]['source']
            if self.music_data[server_id]['vc'] is None or not self.music_data[server_id]['vc'].is_connected():
                self.music_data[server_id]['vc'] = await self.music_data[server_id]['queue'][0][1].connect()
                if self.music_data[server_id]['vc'] is None:
                    await ctx.send("```Could not connect to the voice channel```")
                    return
            else:
                await self.music_data[server_id]['vc'].move_to(self.music_data[server_id]['queue'][0][1])
            self.music_data[server_id]['queue'].pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url, download=False))
            song = data['url']
            self.music_data[server_id]['vc'].play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe", **self.FFMPEG_OPTIONS), after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
        else:
            self.music_data[server_id]['is_playing'] = False

    @commands.command(name="play", aliases=["p", "playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except AttributeError:
            await ctx.send("```You need to connect to a voice channel first!```")
            return
        
        server_id = ctx.guild.id
        if server_id not in self.music_data:
            self.music_data[server_id] = {
                'is_playing': False,
                'is_paused': False,
                'queue': [],
                'vc': None
            }
        
        if self.music_data[server_id]['is_paused']:
            self.music_data[server_id]['is_paused'] = False
            self.music_data[server_id]['is_playing'] = True
            self.music_data[server_id]['vc'].resume()
        else:
            try:
                song = self.search_yt(query)
                if type(song) == dict:
                    if self.music_data[server_id]['is_playing']:
                        await ctx.send(f"**#{len(self.music_data[server_id]['queue']) + 1} -'{song['title']}'** added to the queue")
                    else:
                        await ctx.send(f"**'{song['title']}'** added to the queue")
                        self.music_data[server_id]['queue'].append([song, voice_channel])
                    if not self.music_data[server_id]['is_playing']:
                        await self.play_music(ctx)
                else:
                    await ctx.send("```Could not find the song. Incorrect format. Playlists or livestreams might be the issue.```")
            except:
                await ctx.send("```Unknown error :(```")
    @commands.command(name="pause", help="Pauses the song")
    @commands.has_permissions(administrator=True)
    async def pause(self, ctx, *args):
        server_id = ctx.guild.id
        if server_id in self.music_data:
            
            allowed_user_id = 840187067887124480
            
            if ctx.author.id == allowed_user_id or ctx.author.guild_permissions.administrator:
                if self.music_data[server_id]['is_playing']:
                    self.music_data[server_id]['is_playing'] = False
                    self.music_data[server_id]['is_paused'] = True
                    self.music_data[server_id]['vc'].pause()
                elif self.music_data[server_id]['is_paused']:
                    self.music_data[server_id]['is_paused'] = False
                    self.music_data[server_id]['is_playing'] = True
                    self.music_data[server_id]['vc'].resume()
            else:
                await ctx.send("```You need administrator rights to use this command :(```")
            
            
    @commands.command(name="resume", aliases=["r"], help="Resumes playing")
    async def resume(self, ctx, *args):
        server_id = ctx.guild.id
        if server_id in self.music_data and self.music_data[server_id]['is_paused']:
            allowed_user_id = 840187067887124480
            
            if ctx.author.id == allowed_user_id or ctx.author.guild_permissions.administrator:
                self.music_data[server_id]['is_paused'] = False
                self.music_data[server_id]['is_playing'] = True
                self.music_data[server_id]['vc'].resume()
            else:
                await ctx.send("```You need administrator rights to use this command :(```")

    @commands.command(name="skip", aliases=["s"], help="Skips the song")
    @commands.has_permissions(administrator=True)
    async def skip(self, ctx):
        server_id = ctx.guild.id
        if server_id in self.music_data and self.music_data[server_id]['vc']:
            allowed_user_id = 840187067887124480
            
            if ctx.author.id == allowed_user_id or ctx.author.guild_permissions.administrator:
                self.music_data[server_id]['vc'].stop()
                await self.play_music(ctx)
            else:
                await ctx.send("```You need administrator rights to use this command :(```")

    @commands.command(name="queue", aliases=["q"], help="Shows queue")
    async def queue(self, ctx):
        server_id = ctx.guild.id
        if server_id in self.music_data:
            retval = ""
            for i in range(len(self.music_data[server_id]['queue'])):
                retval += f"#{i+1} - {self.music_data[server_id]['queue'][i][0]['title']}\n"

            if retval:
                await ctx.send(f"```Queue:\n{retval}```")
            else:
                await ctx.send("```No music in queue```")

    @commands.command(name="clear", aliases=["c", "bin"], help="Clears queue and leaves")
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx):
        server_id = ctx.guild.id
        if server_id in self.music_data:
            allowed_user_id = 840187067887124480
            
            if ctx.author.id == allowed_user_id or ctx.author.guild_permissions.administrator:
                if self.music_data[server_id]['vc'] and self.music_data[server_id]['is_playing']:
                    self.music_data[server_id]['vc'].stop()
                self.music_data[server_id]['queue'] = []
                await ctx.send("```Music queue cleared```")
            else:
                await ctx.send("```You need administrator rights to use this command :(```")
                
    @commands.command(name="stop", aliases=["disconnect", "l", "d"], help="Bot leaves from VC")
    @commands.has_permissions(administrator=True)
    async def stop(self, ctx):
        server_id = ctx.guild.id
        if server_id in self.music_data:
            allowed_user_id = 840187067887124480
            
            if ctx.author.id == allowed_user_id or ctx.author.guild_permissions.administrator:
                self.music_data[server_id]['is_playing'] = False
                self.music_data[server_id]['is_paused'] = False
                if self.music_data[server_id]['vc']:
                    await self.music_data[server_id]['vc'].disconnect()
                    self.music_data[server_id]['vc'] = None
            else:
                await ctx.send("```You need administrator rights to use this command :(```")

    @commands.command(name="remove", help="Removes last queued song")
    @commands.has_permissions(administrator=True)
    async def remove(self, ctx):
        server_id = ctx.guild.id
        if server_id in self.music_data and self.music_data[server_id]['queue']:
            allowed_user_id = 840187067887124480
            
            if ctx.author.id == allowed_user_id or ctx.author.guild_permissions.administrator:
                self.music_data[server_id]['queue'].pop()
                await ctx.send("```Last song removed```")
            else:
                await ctx.send("```You need administrator rights to use this command :(```")

async def setup(bot):
    await bot.add_cog(MusicCog(bot))
