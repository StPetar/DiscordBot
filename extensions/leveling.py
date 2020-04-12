import math
import discord
from discord.ext import commands
import sqlite3

exp_per_msg = 2
coin_per_lvl = 5


# New - The Cog class must extend the commands.Cog class
class Leveling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id, exp, lvl, coins FROM levels "
                       f"WHERE guild_id = '{message.author.guild.id}'"
                       f"AND user_id = '{message.author.id}'")
        result = cursor.fetchone()
        if result is None:
            sql = (f"INSERT INTO levels(guild_id, user_id, exp, lvl, coins)"
                   f"VALUES(?, ?, ?, ?, ?)")
            val = (message.author.guild.id, message.author.id, exp_per_msg, 0, 0)
            cursor.execute(sql, val)
            db.commit()
        else:
            exp = int(result[1]) + exp_per_msg
            lvl_start = int(result[2])
            required_xp = math.floor(5 * (lvl_start ** 2) + 50 * lvl_start + 100)
            coins = int(result[3])
            if required_xp < exp:
                lvl_start = lvl_start + 1
                coins = int(result[3]) + coin_per_lvl

                await message.channel.send(
                    f'🔥 **{message.author.mention}** has just advanced to level **{lvl_start}**! 🔥\n'
                    f'          💰 You have also earned 5 coins 💰')

            sql = "UPDATE levels SET exp = ?, lvl = ?, coins = ? WHERE guild_id = ? AND user_id = ?"
            val = (exp, lvl_start, coins, str(message.author.guild.id), str(message.author.id))
            cursor.execute(sql, val)
            db.commit()

    @commands.command(
        name='stats',
        description='Check out your stats',
        aliases=['rank', 'level', 'lvl'],
        usage='<command prefix>stats'
    )
    async def stats_command(self, ctx, user: discord.User = None):
        print(user)
        if user is not None:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(
                f"SELECT user_id, exp, lvl, coins FROM levels "
                f"WHERE guild_id = '{ctx.message.guild.id}' "
                f"AND user_id = '{user.id}'")
            result = cursor.fetchone()
            print(result)

            if result is None:
                await ctx.send(
                    f'{user.name} has not yet been ranked. They need to send a message in the chat first! 👺')
            else:
                lvl_start = int(result[2])
                required_xp = math.floor(5 * (lvl_start ** 2) + 50 * lvl_start + 100)
                remaining_exp = required_xp - int(result[1])
                print(result)
                await ctx.send(
                    f'{user.name} is currently Level {result[2]} - {remaining_exp} exp remaining until next Level \n'
                    f'Also has 💰 {result[3]} Coins in his pocket!')
            cursor.close()
            db.close()
        elif user is None:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(
                f"SELECT user_id, exp, lvl, coins FROM levels "
                f"WHERE guild_id = '{ctx.message.guild.id}' "
                f"AND user_id = '{ctx.message.author.id}'")
            result = cursor.fetchone()
            print(result)

            if result is None:
                await ctx.send(
                    f'{ctx.message.author} has not yet been ranked. They need to send a message in the chat first! 👺')
            else:
                lvl_start = int(result[2])
                required_xp = math.floor(5 * (lvl_start ** 2) + 50 * lvl_start + 100)
                remaining_exp = required_xp - int(result[1])
                await ctx.send(
                    f'{ctx.message.author} is currently Level {result[2]} - {remaining_exp} exp remaining until next Level \n'
                    f'Also has 💰 {result[3]} Coins in his pocket!')
            cursor.close()
            db.close()


def setup(bot):
    bot.add_cog(Leveling(bot))  # Adds the Basic commands to the bot
