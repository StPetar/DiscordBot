from discord.ext import commands
import discord
import random

class Embed(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    # Since I really enjoyed making the bots replies as embeded messages
    # I decided to create a command so users can easily create embeds too
    # With chat prompts for title and message
    @commands.command(
        name='embed',
        description='Create an Embedded message with title and content fields',
    )
    async def embed_command(self, ctx):
        # Define a check function that validates the message received by the bot
        def check(ms):
            # Look for the message sent in the same channel where the command was used
            # As well as by the user who used the command.
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        # First ask the user for the title
        await ctx.send(content='What would you like the title to be?')

        # Wait for a response and get the title
        msg = await self.bot.wait_for('message', check=check)
        title = msg.content  # Set the title

        # Next, ask for the content
        await ctx.send(content='What would you like the Description to be?')
        msg = await self.bot.wait_for('message', check=check)
        desc = msg.content

        # Finally make the embed and send it
        msg = await ctx.send(content='Now generating the embedded message...')

        color_list = [c for c in colors.values()]
        # Convert the colors into a list
        # To be able to use random.choice on it

        embed = discord.Embed(
            title=title,
            description=desc,
            color=random.choice(color_list)
        )
        # Also set the thumbnail to be the bot's pfp
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        # Also set the embed author to the command user
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )

        await msg.edit(
            embed=embed,
            content=None
        )
        # Editing the message
        # We have to specify the content to be 'None' here
        # Since we don't want it to stay to 'Now generating embed...'

        return
    
    # Custom help command, I also removed the original discord help command, check bot.py for that
    @commands.command(
        name='help',
        description='The help command!',
        aliases=['commands', 'command'],
        usage='help *extension/cog list*'
    )
    async def help_command(self, ctx, cog='all'):
        # The third parameter comes into play when
        # only one word argument has to be passed by the user

        # Prepare the embed
        color_list = [c for c in colors.values()]
        help_embed = discord.Embed(
            title='Help',
            color=random.choice(color_list)
        )
        help_embed.set_thumbnail(url=self.bot.user.avatar_url)
        help_embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=self.bot.user.avatar_url
        )

        # Get a list of all cogs
        cogs = [c for c in self.bot.cogs.keys()]

        # If a cog is not specified by the user, we list all cogs and commands
        if cog == 'all':
            for cog in cogs:
                # Get a list of all commands under each cog
                cog_commands = self.bot.get_cog(cog).get_commands()
                commands_list = ''
                for comm in cog_commands:
                    commands_list += f'**{comm.name}** - *{comm.description}*\n'

                # Add the cog's details to the embed.
                help_embed.add_field(
                    name=cog,
                    value=commands_list,
                    inline=False
                )
            pass
        else:

            # If the cog was specified
            lower_cogs = [c.lower() for c in cogs]

            # If the cog actually exists.
            if cog.lower() in lower_cogs:

                # Get a list of all commands in the specified cog
                commands_list = self.bot.get_cog(cogs[lower_cogs.index(cog.lower())]).get_commands()
                help_text = ''

                # Add details of each command to the help text
                # Command Name
                # Description
                # [Aliases]
                #
                # Format
                for command in commands_list:
                    help_text += f'```{command.name}```' \
                                 f'**{command.description}**\n'

                    # Also add aliases, if there are any
                    if len(command.aliases) > 0:
                        help_text += f'*Also usable as: `{"`, `".join(command.aliases)}`*\n'

                    # Finally the format
                    help_text += f'How to use: **{command.usage if command.usage is not None else ""}**\n\n'
                help_embed.description = help_text
            else:
                # Notify the user of invalid cog and finish the command
                await ctx.send('Invalid cog specified.\nUse `help` command to list all cogs.')
                return

        await ctx.send(embed=help_embed)
        return

    @commands.command(
        name='info',
        description='Show bot info',
        aliases=['i']
    )
    # Set up custom bot info
    async def info_command(self, ctx):
        color_list = [c for c in colors.values()]
        info_embed = discord.Embed(
            title='Info',
            color=random.choice(color_list)
        )
        info_embed.set_thumbnail(url=self.bot.user.avatar_url)
        info_embed.set_footer(
            text=f'Requested by {ctx.message.author.name}',
            icon_url=self.bot.user.avatar_url
        )
        # Arbitrary info can be added using fields
        info_embed.add_field(
            name='Author',
            value='The Pesh',
            inline=False
        )
        info_embed.add_field(
            name="Description",
            value=''' 
    A dumbass made me\n
    Available prefixes to use with commands:\n
    =, ==, -, ., !, $, ?, -
    ''',
            inline=False
        )
        await ctx.send(embed=info_embed)
        return
    
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


def setup(bot):
    bot.add_cog(Embed(bot))  # Adds the commands to the bot
