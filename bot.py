import os
import discord
import random
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()
client = commands.Bot(command_prefix='!')


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    greetings = ['hi', 'hello', 'sup', 'yo']

    for greeting in greetings:
        if greeting in message.content:
            await message.channel.send(f"Hello {message.author}!")


@client.event
async def on_member_join(member):
    channel = client.get_channel(697808268818645014)
    print(member.nick)
    await channel.send(f'{member} has joined the server!')


@client.event
async def on_member_remove(member):
    channel = client.get_channel(697808268818645014)

    await channel.send(f'{member.nick} ({member}) has left the server ;(')


@client.command()
async def ping(ctx):
    await ctx.send('Pong!')


@client.command(aliases=['8ball'])
async def _8ball(ctx, *, question):
    await ctx.send('Pong!')
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

    client.run(TOKEN)
