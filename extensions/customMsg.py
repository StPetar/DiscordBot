import sqlite3
import discord
from discord.ext import commands

# This cog is used to select the channel for the custom join and leave messages
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
        # Check a level of administrator permissions, in my case this is just to manage_messages
        # But there are a handful stricter permissions this can be changed to depending on your needs
        if ctx.message.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f'SELECT channel_id FROM main WHERE guild_id = {ctx.guild.id}')
            result = cursor.fetchone()
            
            # If the channel is not already set, set it here
            if result is None:
                sql = 'INSERT INTO main(guild_id, channel_id) VALUES(?, ?)'
                val = (ctx.guild.id, channel.id)
                cursor.execute(sql, val)
                db.commit()
                await ctx.send(f"Channel has been set to {channel.mention}")
                
            # If the channel had been set, update it to the new one
            elif result is not None:
                sql = 'UPDATE main SET channel_id = ? WHERE guild_id = ?'
                val = (channel.id, ctx.guild.id)
                cursor.execute(sql, val)
                db.commit()
                await ctx.send(f'Channel has been updated to {channel.mention}')
            cursor.close()
            db.close()
        return

    # With this command you can have a custom normal message set
    # I however opted to later on remake this into an embedded message
    # So this command is currently unused in my code, check bot.py
    @commands.command(
        name='set_message',
        description='Set custom join message [currently disabled]',
        aliases=['set_msg', 'set_join_msg'],
        usage='<command prefix>set_message [text]'
    )
    async def msg(self, ctx, *, text):
        # Similar to the get_channel command
        # Check for permissions of the user trying to use the command
        if ctx.message.author.guild_permissions.manage_messages:
            db = sqlite3.connect('main.sqlite')
            cursor = db.cursor()
            cursor.execute(f'SELECT msg FROM main WHERE guild_id = {ctx.guild.id}')
            result = cursor.fetchone()
            # Create an entry into the DB if it didn't exist
            if result is None:
                sql = 'INSERT INTO main(guild_id, channel_id) VALUES(?, ?)'
                val = (ctx.guild.id, text)
                cursor.execute(sql, val)
                db.commit()
                await ctx.send(f"Channel has been set to '{text}'")
            # If it did exist, update the entry
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
