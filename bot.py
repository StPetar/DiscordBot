import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    greetings =['hi', 'hello', 'sup', 'yo']

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

client.run(TOKEN)
