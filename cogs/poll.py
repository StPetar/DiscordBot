import discord
from discord.ext import commands


# New - The Cog class must extend the commands.Cog class
class Poll(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    """"""

    @commands.command(
        name='poll',
        description='Create a poll',
        usage='<command prefix>TITLE, Option1, Option2, Option3.... max 10 options'
    )
    async def quickpoll(self, ctx, options=None, *inputs: str):
        for input in inputs:
            options +=" " + input
            print(options)

        list_of_answers = options.split(',')
        if len(list_of_answers) <= 1:
            await ctx.send('You need more than one option to make a poll!')
            return
        if len(list_of_answers) > 10:
            await ctx.send('You cannot make a poll for more than 10 things!')
            return

        if len(list_of_answers) == 2 and list_of_answers[0] == 'yes' and list_of_answers[1] == 'no':
            reactions = ['✅', '❌']
        else:
            reactions = ['1⃣', '2⃣', '3⃣', '4⃣', '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

        description = []
        for x, option in enumerate(list_of_answers):
            description += '\n \n {} {}'.format(reactions[x], option)
        embed = discord.Embed(title=list_of_answers[0], description=''.join(description))
        react_message = await ctx.send(embed=embed)
        for reaction in reactions[:len(list_of_answers)]:
            await react_message.add_reaction(reaction)
        embed.set_footer(text='Poll ID: {}'.format(react_message.id))
        await react_message.edit(
            embed=embed,
        )


def setup(bot):
    bot.add_cog(Poll(bot))  # Adds the Basic commands to the bot
