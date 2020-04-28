# Code mostly sourced from EvieePy, vbe0201 and Rapptz and personal revision
# https://gist.github.com/EvieePy/ab667b74e9758433b3eb806c53a19f34
# https://gist.github.com/vbe0201/ade9b80f2d3b64643d854938d40a0a2d
# https://github.com/Rapptz/discord.py


import asyncio
import functools
import itertools
import math
import random
import discord
import youtube_dl
from async_timeout import timeout
from discord.ext import commands

youtube_dl.utils.bug_reports_message = lambda: ''


class YTDLError(Exception):
    pass


class MusicError(Exception):
    pass


class YTDLSource(discord.PCMVolumeTransformer):
    ytdl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'max-downloads': '25'
    }

    ffmpeg_opts = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

    ytdl = youtube_dl.YoutubeDL(ytdl_opts)

    def __init__(self, message, source, *, data, volume=0.02):
        super().__init__(source, volume)

        self.requester = message.author
        self.channel = message.channel
        self.data = data

        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')
        self.upload_date = f'{data.get("upload_date")[6:8]}.{data.get("upload_date")[4:6]}.{data.get("upload_date")[0:4]}'
        self.title = data.get('title')
        self.thumbnail = data.get('thumbnail')
        self.description = data.get('description')
        self.duration = self.parse_duration(int(data.get('duration')))
        self.tags = data.get('tags')
        self.url = data.get('webpage_url')
        self.views = data.get('view_count')
        self.likes = data.get('like_count')
        self.dislikes = data.get('dislike_count')
        self.stream_url = data.get('url')

    def __str__(self):
        return f'**{self.title}** by **{self.uploader}** *[Duration: {self.duration}]*'

    @classmethod
    async def create_source(cls, message, search: str, *, loop=None):
        loop = loop or asyncio.get_event_loop()

        partial = functools.partial(cls.ytdl.extract_info, search, download=False, process=False)
        data = await loop.run_in_executor(None, partial)

        if data is None:
            raise YTDLError(f'Couldn\'t find anything that matches the search query `{search}`')

        if 'entries' not in data:
            process_info = data
        else:
            process_info = None
            for entry in data['entries']:
                if entry is not None:
                    process_info = entry
                    break

            if process_info is None:
                raise YTDLError(f'Couldn\'t retrieve any data for the search query `{search}`')

        webpage_url = process_info['webpage_url']
        partial = functools.partial(cls.ytdl.extract_info, webpage_url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        if processed_info is None:
            raise YTDLError(f'Error while trying to fetch the data for the url `{webpage_url}`')

        if 'entries' not in processed_info:
            info = processed_info
        else:
            info = None
            while info is None:
                try:
                    info = processed_info['entries'].pop(0)
                except IndexError:
                    raise YTDLError(f'Couldn\'t retrieve any matches for the url `{webpage_url}`')

        return cls(message, discord.FFmpegPCMAudio(info['url'], **cls.ffmpeg_opts), data=info)

    @staticmethod
    def parse_duration(duration: int):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)

        # Create an actual string
        duration = []
        if days > 0:
            duration.append(f'{days} days')
        if hours > 0:
            duration.append(f'{hours} hours')
        if minutes > 0:
            duration.append(f'{minutes} minutes')
        if seconds > 0:
            duration.append(f'{seconds} seconds')

        return ', '.join(duration)


class Song:
    def __init__(self, state, source):
        self.state = state
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = discord.Embed(title='Now playing:', description=f'```css\n{self.source.title}\n```',
                              color=discord.Color.green())

        embed.add_field(name='Duration:', value=self.source.duration)
        embed.add_field(name='Requested by:', value=self.requester.mention)
        embed.add_field(name='Uploader:', value=f'[{self.source.uploader}]({self.source.uploader_url})')
        embed.add_field(name='Song URL:', value=f'[Click here]({self.source.url})')
        embed.set_thumbnail(url=self.source.thumbnail)

        return embed


class SongQueue(asyncio.Queue):
    def __iter__(self):
        return self._queue.__iter__()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, value: int):
        self._queue.rotate(-value)
        self._queue.pop()
        self._queue.rotate(value - 1)

    def __getitem__(self, index):
        if isinstance(index, slice):
            return list(itertools.islice(self._queue, index.start, index.stop, index.step))
        else:
            return self._queue[index]

    def __len__(self):
        return len(self._queue)


class VoiceState:
    def __init__(self, bot, ctx):
        self.current = None
        self.voice = None
        self._volume = 0.02
        self.bot = bot
        self._ctx = ctx
        self.next = asyncio.Event()
        self.songs = SongQueue()
        self.skip_votes = set()
        self.audio_player = bot.loop.create_task(self.audio_player_task())

    async def audio_player_task(self):
        while True:
            self.next.clear()

            # Try to get a song within the next few minutes.
            # If no song will be added to the queue in time,
            # the player will disconnect due to performance
            # reasons.
            try:
                async with timeout(300):  # 5 minutes
                    self.current = await self.songs.get()
            except asyncio.TimeoutError:
                return self.bot.loop.create_task(self.stop())

            self.current.source.volume = self._volume
            self.voice.play(self.current.source, after=self.play_next_song)
            await self.current.source.channel.send(embed=self.current.create_embed())

            await self.next.wait()

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value

        if self.voice:
            self.voice.source.volume = value

    def is_done(self):
        if self.voice is None or self.current is None:
            return True

        return not self.voice.is_playing() and not self.voice.is_paused()

    def play_next_song(self, error=None):
        fut = asyncio.run_coroutine_threadsafe(self.next.set(), self.bot.loop)

        try:
            fut.result()
        except:
            raise MusicError(error)

    def skip(self):
        self.skip_votes.clear()

        if not self.is_done():
            self.voice.stop()

    async def stop(self):
        self.songs.clear()

        if self.voice:
            await self.voice.disconnect()
            self.voice = None


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx):
        state = self.voice_states.get(ctx.guild.id)

        if state is None:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx):
        if not ctx.guild:
            raise commands.NoPrivateMessage('This command can\'t be used in a DM channel.')

        return True

    async def cog_before_invoke(self, ctx):
        ctx.state = self.get_voice_state(ctx)

    async def cog_command_error(self, ctx, error):
        # This kind of error handling is not really good. It's simple and functional, but not good.
        # I'd recommend to extend this.
        await ctx.send(error)

    @commands.command(
        name='join',
        invoke_without_command=True,
        description="Join the user's voice channel",
        usage='<command prefix>join',
        aliases=['j'])
    async def _join(self, ctx):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel

        if ctx.state.voice is not None:
            return await ctx.state.voice.move_to(destination)

        ctx.state.voice = await destination.connect()

    @commands.command(
        name='summon',
        description="Summon the bot to a voice channel.\n If no channel is given it joins the user's channel",
        usage='<command prefix>summon {voice channel name}')
    @commands.has_permissions(manage_guild=True)
    async def _summon(self, ctx, *, channel: discord.VoiceChannel = None):
        """Summons the bot to a voice channel. If no channel given, it joins your channel."""

        if channel is None and not ctx.author.voice:
            raise MusicError('You are not connected to a voice channel nor specified a channel to join.')

        destination = channel or ctx.author.voice.channel

        if ctx.state.voice is not None:
            return await ctx.state.voice.move_to(destination)

        ctx.state.voice = await destination.connect()

    @commands.command(
        name='play',
        description="Play a song, currently doesn't support whole playlists",
        usage='<command prefix>play {Artist} {Song name} or <command prefix>play {Song Youtube url}',
        aliases=['p'])
    async def _play(self, ctx, *, search: str):
        """Plays a song.
        If there are currently songs in the queue then it is queued until the next song is done playing.
        This command automatically searches from YouTube as well.
        A list of supported sites can be found here: https://rg3.github.io/youtube-dl/supportedsites.html
        """

        if ctx.state.voice is None:
            await ctx.invoke(self._join)

        async with ctx.typing():
            try:
                source = await YTDLSource.create_source(ctx.message, search, loop=self.bot.loop)
            except Exception as e:
                await ctx.send(f'An error occurred while processing this request: {e}')
            else:
                song = Song(ctx.state.voice, source)

                await ctx.state.songs.put(song)
                await ctx.send(f'Enqueued {str(source)}')

    @commands.command(
        name='volume',
        aliases=['vol'],
        description="Change bot volume",
        usage='<command prefix>volume {0-100%}')
    async def _volume(self, ctx, *, volume: int):
        """Sets the volume of the currently playing song."""

        if ctx.state.is_done():
            return await ctx.send('Nothing playing at the moment.')

        if 0 > volume > 100:
            return await ctx.send('Volume must be between 0 and 100.')

        ctx.state.volume = volume / 100
        await ctx.send(f'The player\'s volume was set to {volume}%')

    @commands.command(
        name='now',
        aliases=['playing', 'current'],
        description="Display currently playing song in chat",
        usage='<command prefix>now'
    )
    async def _now(self, ctx):
        """Displays the currently playing song."""

        await ctx.send(embed=ctx.state.current.create_embed())

    @commands.command(
        name='pause',
        description="Pause currently playing song",
        usage='<command prefix>pause'
    )
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx):
        """Pauses the currently playing song."""

        if not ctx.state.is_done():
            ctx.state.voice.pause()
            # await ctx.message.add_reaction('⏯')

    @commands.command(
        name='resume',
        description="Resume paused song",
        usage='<command prefix>resume'
    )
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx):
        """Resumes a currently paused song."""

        if not ctx.state.is_done():
            ctx.state.voice.resume()
            # await ctx.message.add_reaction('⏯')

    @commands.command(
        name='stop',
        description="Stop bot and clear the queue",
        usage='<command prefix>stop'
    )
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx):
        """Stops playing audio and clears the queue."""

        ctx.state.songs.clear()

        if not ctx.state.is_done():
            ctx.state.voice.stop()
            # await ctx.message.add_reaction('⏹')

    @commands.command(
        name='skip',
        description="Vote to skip a song. The requester can automatically skip.\n \
         3 skip votes are needed for the song to be skipped.",
        usage='<command prefix>skip'
    )
    async def _skip(self, ctx):
        """Vote to skip a song. The requester can automatically skip.
        3 skip votes are needed for the song to be skipped.
        """

        if ctx.state.is_done():
            raise MusicError('Not playing any music right now...')

        voter = ctx.message.author
        if voter == ctx.state.current.requester:
            await ctx.message.add_reaction('⏭')
            ctx.state.skip()

        elif voter.id not in ctx.state.skip_votes:
            ctx.state.skip_votes.add(voter.id)
            total_votes = len(ctx.state.skip_votes)

            if total_votes >= 3:
                await ctx.message.add_reaction('⏭')
                ctx.state.skip()
            else:
                await ctx.send(f'Skip vote added, currently at **{total_votes}/3**')

        else:
            await ctx.send('You have already voted to skip this song.')

    @commands.command(
        name='queue',
        aliases=['q'],
        description="Display current queue in chat",
        usage='<command prefix>queue'
    )
    async def _queue(self, ctx, *, page: int = 1):
        """Shows the player's queue."""

        if len(ctx.state.songs) == 0:
            raise MusicError('Nothing in the queue.')

        items_per_page = 10
        pages = math.ceil(len(ctx.state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ''
        for index, song in enumerate(ctx.state.songs[start:end], start=start):
            queue += f'`{index + 1}.` [**{song.source.title}**]({song.source.url})\n'

        embed = discord.Embed(color=discord.Color.green(), description=f'**{len(ctx.state.songs)} tracks:**\n\n{queue}')
        embed.set_footer(text=f'Viewing page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(
        name='shuffle',
        description="Shuffle the current queue",
        usage='<command prefix>shuffle'
    )
    async def _shuffle(self, ctx):
        """Shuffles the current queue."""

        if len(ctx.state.songs) == 0:
            raise MusicError('Nothing in the queue.')

        ctx.state.songs.shuffle()
        await ctx.send('The queue has been shuffled')
        new_queue = await self._queue(ctx)
        return new_queue

    @commands.command(
        name='remove',
        aliases=['rem', 'r'],
        description="Remove a song from the queue with the given index",
        usage='<command prefix>remove [index of song]'
    )
    async def _remove(self, ctx, index: int):
        """Removes an item from the queue with the given index."""

        # Please refer from using this command as well as the remove method of SongQueue class.
        # I implemented this just for completeness.
        # But as you may have noticed, asyncio.Queue uses a dequeue to actually store the objects.
        # It's not the sense behind a dequeue to sort out items at specific indexes.
        # If this is what you want to do, you might better use a different data structure like a list.

        if len(ctx.state.songs) == 0:
            raise MusicError('Nothing in the queue.')

        ctx.state.songs.remove(index)
        await ctx.message.add_reaction('✅')

    @commands.command(
        name='disconnect',
        aliases=['leave', 'l'],
        description="The bot clears the song queue and leaves the channel",
        usage='<command prefix>disconnect'
    )
    @commands.has_permissions(manage_guild=True)
    async def _disconnect(self, ctx):
        """Clears the queue and leaves the voice channel."""

        if ctx.state.voice is None:
            raise MusicError('Not connected to any voice channel.')
        await ctx.state.stop()

    @_join.before_invoke
    @_play.before_invoke
    async def ensure_voice(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandError('You are not connected to any voice channel.')

        if ctx.voice_client is not None:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                raise MusicError('Bot already in a voice channel.')


def setup(bot):
    bot.add_cog(Music(bot))  # Adds the Basic commands to the bot
