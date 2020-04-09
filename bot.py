import os
import discord
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
bot_channel = 697808268818645014  # copy ID from Discord
bot = commands.Bot(command_prefix='.')


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(
        activity=discord.Game(
            name=f"Use {bot.command_prefix} to interact with me!"))  # Changes bot activity


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(bot_channel)
    print(member.nick)
    await channel.send(f'{member} has joined the server!')  # Announce member joining


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(bot_channel)

    await channel.send(f'{member.nick} ({member}) has left the server ;(')  # Announce member leaving


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong!, {ctx.author}')  # Ping Pong game


@bot.command(pass_context=True, aliases=['hi', 'hey', 'sup', 'yo'])
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author}!")  # Handles greetings


@bot.command()  # 8ball game
async def _8ball(ctx, *, question):
    responses = ['As I see it, yes.',
                 ' Ask again later.',
                 ' Better not tell you now.',
                 'Cannot predict now.',
                 ' Concentrate and ask again.',
                 ' Don’t count on it.',
                 ' It is certain.',
                 'It is decidedly so.',
                 ' Most likely.',
                 ' My reply is no.',
                 ' My sources say no.',
                 ' Outlook not so good.',
                 ' Outlook good.',
                 ' Reply hazy, try again.',
                 ' Signs point to yes.',
                 ' Very doubtful.',
                 ' Without a doubt.',
                 ' Yes.',
                 ' Yes – definitely.',
                 ' You may rely on it.']
    await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')


bot.run(os.getenv('DISCORD_TOKEN'))
