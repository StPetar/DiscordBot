import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
bot_channel = 415919199760941058  # copy ID from Discord
spit_chanel = 697802630923157638  # test server general channel


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
cogs = ['cogs.basic', 'cogs.embed']  # Load files from cogs directory


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.change_presence(
        activity=discord.Game(
            name="with myself"))  # Changes bot activity
    bot.remove_command('help')  # Removes the help command
    for cog in cogs:
        bot.load_extension(cog)
    return


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(bot_channel)
    print(member.nick)
    await channel.send(f'{member} has joined the server!')  # Announce member joining


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(bot_channel)

    await channel.send(f'{member.nick} ({member}) has left the server ;(')  # Announce member leaving


# @bot.event
# async def job():
#     channel = bot.get_channel(bot_channel)
#     await channel.send('@zhekoff#4341 :PepeSpit:')
#     await schedule.every(5).seconds.do(job)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

bot.run(os.getenv('DISCORD_TOKEN'), bot=True, reconnect=True)
