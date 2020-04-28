import math
import random
import time
import discord
from discord.ext import commands
import sqlite3

# Set values to whatever you would like
exp_per_msg = 2
coin_per_lvl = 5


def __init__(self, bot):
    self.bot = bot


# New - The Cog class must extend the commands.Cog class
class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # The listener decorator keeps track of messages without the need to run commands
    async def on_message(self, message):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        # Exp bonuses only for for users which are not the BOT to reduce DB usage
        if message.author.id is not self.bot.user.id:
            # Fetch the user info from the DB
            cursor.execute(f"SELECT user_id, exp, lvl, coins FROM levels "
                           f"WHERE guild_id = '{message.author.guild.id}'"
                           f"AND user_id = '{message.author.id}'")
            result = cursor.fetchone()
            # If the user was not in the DB, add him
            if result is None:
                sql = (f"INSERT INTO levels(guild_id, user_id, exp, lvl, coins)"
                       f"VALUES(?, ?, ?, ?, ?)")
                val = (message.author.guild.id, message.author.id, exp_per_msg, 0, 0)
                cursor.execute(sql, val)
                db.commit()
            else:
                # If the user was in the DB proceed with calculations
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
                # Update user info
                sql = "UPDATE levels " \
                      "SET exp = ?, lvl = ?, coins = ? " \
                      "WHERE guild_id = ? AND user_id = ?"
                val = (exp, lvl_start, coins, str(message.author.guild.id), str(message.author.id))
                cursor.execute(sql, val)
        # Commit changes and close connections to DB
        db.commit()
        cursor.close()
        db.close()

    @commands.command(
        name='stats',
        description='Check out your stats',
        aliases=['level', 'lvl'],
        usage='<command prefix>stats'
    )
    async def stats_command(self, ctx, user: discord.User = None):
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        
        # If the user is specified in the message, fetch his info
        if user is not None:
            cursor.execute(
                f"SELECT user_id, exp, lvl, coins FROM levels "
                f"WHERE guild_id = '{ctx.message.guild.id}' "
                f"AND user_id = '{user.id}'")
            result = cursor.fetchone()
            # Send error in chat if the given user is not in the DB
            if result is None:
                await ctx.send(
                    f'{user.name} has not yet been ranked. They need to send a message in the chat first! 👺')
            # If the given user is in the DB proceed with calculations and output
            else:
                lvl_start = int(result[2])
                required_xp = math.floor(5 * (lvl_start ** 2) + 50 * lvl_start + 100)
                remaining_exp = required_xp - int(result[1])
                await ctx.send(
                    f'{user.name} is currently Level {result[2]} - {remaining_exp} exp remaining until next Level \n'
                    f'Also has 💰 {result[3]} Coins in his pocket!')
                
        # If no user is specified when using the command, fetch the author's info
        elif user is None:
            cursor.execute(
                f"SELECT user_id, exp, lvl, coins FROM levels "
                f"WHERE guild_id = '{ctx.message.guild.id}' "
                f"AND user_id = '{ctx.message.author.id}'")
            result = cursor.fetchone()
            # Error handling
            if result is None:
                await ctx.send(
                    f'{ctx.message.author} has not yet been ranked. They need to send a message in the chat first! 👺')
            # Proceed with calculations and output
            else:
                lvl_start = int(result[2])
                required_xp = math.floor(5 * (lvl_start ** 2) + 50 * lvl_start + 100)
                remaining_exp = required_xp - int(result[1])
                await ctx.send(
                    f'{ctx.message.author} is currently Level {result[2]} - {remaining_exp} exp remaining until next Level \n'
                    f'Also has 💰 {result[3]} Coins in his pocket!')
        cursor.close()
        db.close()

    @commands.Cog.listener()
    # Another listener, this time keeping track of users time spent in voice channels
    # I introduced this as another way to earn EXP on my server
    # As only EXP on messages would likely result in spam
    async def on_voice_state_update(self, member, before, after):
        # Ignore bot activity as I'd like to keep the rankings only for actual users
        # And the bot having multiple answers to commands and spending time in voice channels for music
        # Would result in it likely topping said rankings eventually
        if member.id is not self.bot.user.id:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            # Fetch user info
            cursor.execute(f"SELECT user_id, exp, lvl, coins FROM levels "
                           f"WHERE guild_id = '{member.guild.id}'"
                           f"AND user_id = '{member.id}'")
            result = cursor.fetchone()
            # If the user hadn't typed anything in chat so far and is not in the DB, add him
            if result is None:
                sql = (f"INSERT INTO levels(guild_id, user_id, exp, lvl, coins)"
                       f"VALUES(?, ?, ?, ?, ?)")
                val = (member.guild.id, member.id, exp_per_msg, 0, 0)
                cursor.execute(sql, val)
                db.commit()
            print(f"Update in {member.guild}, {member} {before.channel} -> {after.channel}")
            # If user was in a NON VOICE channel before and moved into a VOICE channel
            if before.channel is None:
                #Record the time when the user joined and update it in the DB
                start_time = time.time()
                sql = (f'UPDATE levels '
                       f'SET time_join = ? '
                       f'WHERE guild_id = ? AND user_id = ?')
                val = (start_time, member.guild.id, member.id)
                cursor.execute(sql, val)
                db.commit()
            # Fetch user's info when he leaves a voice channel
            if after.channel is None and before.channel is not None:
                # Fetch bot channel from DB (This is where all bot answers are sent to, check extensions/customMsg.py)
                cursor.execute(f'SELECT channel_id FROM main WHERE guild_id = {member.guild.id}')
                result = cursor.fetchone()
                channel = member.guild.get_channel(int(result[0]))
                # Fetch user info
                cursor.execute(
                    f'SELECT user_id, exp, lvl, time_join, coins '
                    f'FROM levels '
                    f'WHERE guild_id = {member.guild.id} AND user_id = {member.id}')
                result = cursor.fetchone()
                # Record the time when the user left and calculate rewards
                end_time = time.time()
                elapsed_time = end_time - result[3]
                time_spent = f'{round(elapsed_time / 60)}min {round(elapsed_time % 60, 2)}sec'
                print(f'{member} spent {time_spent} in a voice channel')
                min_in_channel = (round(elapsed_time) / 60)
                reward = math.floor((min_in_channel / 5) * 2)
                # Send chat message stating rewards and time spent in the voice channel
                await channel.send(
                    f'🔥 **{member.mention}** has been awarded {reward} exp for spending {time_spent} in a voice channel! 🔥')
                
                exp = int(result[1]) + reward
                lvl_start = int(result[2])
                required_xp = math.floor(5 * (lvl_start ** 2) + 50 * lvl_start + 100)
                coins = int(result[4])
                # Only if user leveled up
                if required_xp < exp:
                    lvl_start = lvl_start + 1
                    coins = coins + coin_per_lvl

                    await channel.send(
                        f'🔥 **{member.mention}** has just advanced to level **{lvl_start}**! 🔥\n'
                        f'          💰 You have also earned 5 coins 💰')

                    sql = "UPDATE levels " \
                          "SET exp = ?, lvl = ?, coins = ? " \
                          "WHERE guild_id = ? AND user_id = ?"
                    val = (exp, lvl_start, coins, str(member.guild.id), str(member.id))
                    cursor.execute(sql, val)
                    db.commit()
                else:
                    # Update only the exp as it's the only thing that changed
                    sql = "UPDATE levels " \
                          "SET exp = ?" \
                          "WHERE guild_id = ? AND user_id = ?"
                    val = (exp, lvl_start, coins, str(member.guild.id), str(member.id))
                    cursor.execute(sql, val)
                    db.commit()
            cursor.close()
            db.close()

    @commands.command(
        name='leaderboard',
        description='View the leaderboard',
        aliases=['board', 'ranking', 'ranks'],
        usage='<command prefix>leaderboard'
    )
    async def leaderboard_command(self, ctx):
        color_list = [c for c in colors.values()]
        db = sqlite3.connect('main.sqlite')
        cursor = db.cursor()
        # Fetch all users info in descending order by EXP
        cursor.execute(
            f"SELECT user_id, exp, lvl, coins "
            f"FROM levels "
            f"WHERE guild_id = '{ctx.message.guild.id}'"
            f"ORDER BY exp desc")
        result = cursor.fetchall()
        if result is None:
            await ctx.send('**Leaderboard is empty**')
        else:
            # Create a custom embed message
            leaderboard = discord.Embed(
                title='👑 **LEADERBOARD** 👑',
                color=random.choice(color_list)
            )
        user = ''
        total_exp = ''
        level = ''
        
        # Add medals to top 3 users and #Number for every other user
        medals = ['🥈', '🥉', '🥇']
        for number, player in enumerate(result):
            name = await self.bot.fetch_user(int(player[0]))
            if number < 3:
                user += medals[number - 1] + ' ' + str(name) + '\n'
                level += str(player[2]) + '\n'
                total_exp += str(player[1]) + '\n'
            else:
                user += '#' + str(number + 1) + ' ' + str(name) + '\n'
                level += str(player[2]) + '\n'
                total_exp += str(player[1]) + '\n'
        # Add inline fields for each users in the ranking
        leaderboard.add_field(name='__**Rank and Username**__', value=f'**{user}**', inline=True)
        leaderboard.add_field(name='__**Level**__', value=f'{level}', inline=True)
        leaderboard.add_field(name='__**Total Exp**__', value=f'{total_exp}', inline=True)

        await ctx.send(embed=leaderboard)
        cursor.close()
        db.close()


        # TODO add stuff to buy with coins: exp boosts, roles, name colors ??????

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
    bot.add_cog(Leveling(bot))  # Adds the Basic commands to the bot
