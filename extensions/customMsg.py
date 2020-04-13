import sqlite3
import discord
from discord.ext import commands


class MessageSelect(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        invoke_without_command=True,
        name='bot_channel',
        description='Select text channel for custom join and leave messages',
        aliases=['bot_chnl', 'botchannel'],
        usage='<command prefix>bot_channel #{channel}'
    )
    async def channel_select(self, ctx, channel: discord.TextChannel):
        if ctx.message.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f'SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id}')
            result = cursor.fetchone()
            if result is None:
                sql = 'INSERT INTO main(guild_id, channel_id) VALUES(?, ?)'
                val = (ctx.guild.id, channel.id)
                cursor.execute(sql, val)
                db.commit()
                await ctx.send(f"Channel has been set to {channel.mention}")
            elif result is not None:
                sql = 'UPDATE main SET channel_id = ? WHERE guild_id = ?'
                val = (channel.id, ctx.guild.id)
                cursor.execute(sql, val)
                db.commit()
                await ctx.send(f'Channel has been updated to {channel.mention}')
            cursor.close()
            db.close()
        return

    @commands.command(
        name='set_message',
        description='Set custom join message [currently disabled]',
        aliases=['set_msg', 'set_join_msg'],
        usage='<command prefix>set_message [text]'
    )
    async def msg(self, ctx, *, text):
        if ctx.message.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f'SELECT msg FROM main WHERE guild_id = {ctx.guild.id}')
            result = cursor.fetchone()
            if result is None:
                sql = 'INSERT INTO main(guild_id, channel_id) VALUES(?, ?)'
                val = (ctx.guild.id, text)
                cursor.execute(sql, val)
                db.commit()
                await ctx.send(f"Channel has been set to '{text}'")
            elif result is not None:
                sql = 'UPDATE main SET channel_id = ? WHERE guild_id = ?'
                val = (text, ctx.guild.id)
                cursor.execute(sql, val)
                db.commit()
                await ctx.send(f"Channel has been updated to '{text}'")
            cursor.close()
            db.close()
        return


def setup(bot):
    bot.add_cog(MessageSelect(bot))
