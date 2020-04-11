from discord.ext import commands
from datetime import datetime as d
import random


class Basic(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Define a new command
    @commands.command(
        name='ping',
        description='The ping command',
    )
    async def ping_command(self, ctx):
        start = d.timestamp(d.now())
        # Gets the timestamp when the command was used

        msg = await ctx.send(content='Pinging')
        # Sends a message to the user in the channel the message with the command was received.
        # Notifies the user that pinging has started

        await msg.edit(content=f'Pong!\nOne message round-trip took {round((d.timestamp(d.now()) - start) * 1000)}ms.')
        # Ping completed and round-trip duration show in ms
        # Since it takes a while to send the messages
        # it will calculate how much time it takes to edit an message.
        # It depends usually on your internet connection speed
        return

    @commands.command(
        name='say',
        description='The parrot/repeat command',
        aliases=['repeat', 'parrot'],
        usage='<text>'
    )
    async def say_command(self, ctx):
        # ctx - is the Context related to the command
        # https://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#context

        # Get the message with the command in it.
        msg = ctx.message.content

        # Extracting the text sent by the user
        # ctx.invoked_with gives the alias used
        # ctx.prefix gives the prefix used while invoking the command
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        text = msg[len(prefix_used) + len(alias_used):]

        # Next, we check if the user actually passed some text
        if text == '':
            # User didn't specify the text
            await ctx.send(content='You need to specify the text!')
            pass
        else:
            # User specified the text.
            await ctx.send(content=f"**{text}**")
            pass
        return

    @commands.command(
        name='hello',
        description='Greetings',
        aliases=['hey', 'hi', 'sup', 'yo', 'waddap'],
        usage=''
    )
    async def hello_command(self, ctx):
        await ctx.send(f"Hello {ctx.author}!")  # Handles greetings

    @commands.command(
        name='8ball',
        description='A fortune telling 8ball',
        aliases=['ball', 'fortune'],
        usage='<question>'

    )
    async def ball_command(self, ctx, *, question):  # renamed from _8ball to ball until i learn to code
        responses = [' As I see it, yes.',
                     ' Ask again later.',
                     ' Better not tell you now.',
                     ' Cannot predict now.',
                     ' Concentrate and ask again.',
                     ' Don’t count on it.',
                     ' It is certain.',
                     ' It is decidedly so.',
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


def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
