import os
import random
import aiohttp
import discord
from discord.ext import commands
from dotenv import load_dotenv
import sqlite3

load_dotenv()
bot_channel = 415919199760941058  # copy ID from Discord
spit_chanel = 697802630923157638  # test server general channel
GUILD = os.getenv('DISCORD_GUILD')


def __init__(self, bot):
    self.bot = bot


def get_prefix(client, message):
    prefixes = ['=', '==', '-', '.', '!', '$', '?',
                '-']  # sets the prefixes, u can keep it as an array of only 1 item if you need only one prefix

    # Allow users to @mention the bot instead of using a prefix when using a command. Also optional
    # Do `return prefixes` if u don't want to allow mentions instead of prefix.
    return commands.when_mentioned_or(*prefixes)(client, message)


bot = commands.Bot(  # Create a new bot
    command_prefix=get_prefix,  # Set the prefix

    # Set a description for the bot
    description=''' 
    A dumbass made me\n
    Availble prefixes to use with commands:\n
    =, ==, -, ., !, $, ?, -
    ''',
    owner_id=234381060018929664,  # Your unique User ID
    case_insensitive=True  # Make the commands case insensitive
)
extensions = ['extensions.embed',
              'extensions.basic',
              'extensions.poll',
              'extensions.google',
              'extensions.music',
              'extensions.customMsg',
              'extensions.leveling'
              ]


# Load files from extensions directory


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    bot.session = aiohttp.ClientSession(loop=bot.loop, headers={"User-Agent": "ThePeshBot"})
    await bot.change_presence(
        activity=discord.Game(
            name="with myself"))  # Changes bot activity
    bot.remove_command('help')  # Removes the help command
    for extension in extensions:
        bot.load_extension(extension)
        print(f'{bot.user} has loaded extension {extension}')
    return


@bot.event
async def on_member_join(member):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f'SELECT channel_id FROM main WHERE guild_id = {member.guild.id}')
    result = cursor.fetchone()
    color_list = [c for c in colors.values()]
    if result is None:
        return
    else:
        cursor.execute(f'SELECT msg FROM main WHERE guild_id = {member.guild.id}')
        channel = bot.get_channel(id=int(result[0]))
        members = len(list(member.guild.members))
        if members % 10 == 1:
            msg = str(members) + 'st'
        elif members % 10 == 2:
            msg = str(members) + 'nd'
        else:
            msg = str(members) + 'th'
    # await channel.send(
    #     f'{member} has joined the server! \n{member}, you are the {msg} member!')  # Announce member joining

    join_embed = discord.Embed(
        title='**Greetings!** 🥳',
        color=random.choice(color_list)
    )
    join_embed.set_thumbnail(url=f'{member.avatar_url}')

    join_embed.add_field(
        name=f'**{member}**',
        value='has joined the server!',
        inline=False
    )
    join_embed.add_field(
        name='Member number:',
        value=f'You are the **{msg}** member! ',
        inline=False
    )
    await channel.send(embed=join_embed)


@bot.event
async def on_member_remove(member):
    db = sqlite3.connect('main.sqlite')
    cursor = db.cursor()
    cursor.execute(f'SELECT channel_id FROM main WHERE guild_id = {member.guild.id}')
    result = cursor.fetchone()
    color_list = [c for c in colors.values()]
    if result is None:
        return
    else:
        cursor.execute(f'SELECT msg FROM main WHERE guild_id = {member.guild.id}')
        channel = bot.get_channel(id=int(result[0]))
        members = len(list(member.guild.members))

    leave_embed = discord.Embed(
        title='✝️ Obituary ✝️',
        color=random.choice(color_list)
    )
    leave_embed.set_thumbnail(url=f'{member.avatar_url}')

    leave_embed.add_field(
        name=f'**{member}**',
        value='has left the server 😥',
        inline=False
    )
    leave_embed.add_field(
        name='Member numbers:',
        value=f'We now have {members} members.',
        inline=False
    )
    await channel.send(embed=leave_embed)


# Color constants are taken from discord.js library
colors = {
    'DEFAULT': 0x000000,
    'WHITE': 0xFFFFFF,
    'AQUA': 0x1ABC9C,
    'GREEN': 0x2ECC71,
    'BLUE': 0x3498DB,
    'PURPLE': 0x9B59B6,
    'LUMINOUS_VIVID_PINK': 0xE91E63,
    'GOLD': 0xF1C40F,
    'ORANGE': 0xE67E22,
    'RED': 0xE74C3C,
    'GREY': 0x95A5A6,
    'NAVY': 0x34495E,
    'DARK_AQUA': 0x11806A,
    'DARK_GREEN': 0x1F8B4C,
    'DARK_BLUE': 0x206694,
    'DARK_PURPLE': 0x71368A,
    'DARK_VIVID_PINK': 0xAD1457,
    'DARK_GOLD': 0xC27C0E,
    'DARK_ORANGE': 0xA84300,
    'DARK_RED': 0x992D22,
    'DARK_GREY': 0x979C9F,
    'DARKER_GREY': 0x7F8C8D,
    'LIGHT_GREY': 0xBCC0C0,
    'DARK_NAVY': 0x2C3E50,
    'BLURPLE': 0x7289DA,
    'GREYPLE': 0x99AAB5,
    'DARK_BUT_NOT_BLACK': 0x2C2F33,
    'NOT_QUITE_BLACK': 0x23272A
}
bot.run(os.getenv('DISCORD_TOKEN'))
