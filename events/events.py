from http.client import HTTPException
from unicodedata import name
import discord
from discord.ext import commands
import uttilities
import assets
from datetime import datetime

current_time = datetime.utcnow()

class events(commands.Cog):
    def __init__(self, bot):
        """Event handler"""
        self.bot = bot

    # Member events

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Event to log member joims"""
        logchannel = await self.bot.get_channel(1015733829761241168)
        welcomechannel = await self.bot.get_channel()
        log_embed = discord.Embed(name='Welcome', color = discord.Color.green())
        
        ##  Try sending an userlog embed
        log_embed.add_field(name='Member joined', value=f"{member.name}#{member.discriminator}")
        log_embed.set_author(url = member.avatar_url)
        log_embed.set_footer(text=f"Author ID: {member.id}")
        try:
            await logchannel.send(embed=log_embed)
        except HTTPException:
            return await logchannel.send(f"**Member joined**\n\nMember: {member.name}#{member.discriminator}\n\nMember ID: {member.id}")
    
    @commands.Cog.listener()
    async def on_member_leave(self, member):
        """Event to log member leaves"""
        logchannel = await self.bot.get_channel(1015733829761241168)
        embed = discord.Embed(name='Member Left', color = discord.Color.red())
        try:
            embed.add_field(name='Member left!', value=f"{member.name}#{member.discriminator}")
            embed.set_author(url=member.avatar_url)
            embed.set_footer(text=f"Member ID: {member.id}")
            await logchannel.send(embed = embed)
        except HTTPException:
            return await logchannel.send(f"**Member left**\n\nMember: {member.name}#{member.discriminator}\n\Member ID: {member.id}")
    
    @commands.Cog.listener()
    async def on_member_ban(self, member):
        embed = discord.Embed(name='Member Banned', color = discord.Color.red())
        logchannel = await self.bot.get_channel(1015733829761241168)
        try:
            embed.add_field(name="Member Banned", value=f"{member.name}#{member.discriminator}")
            embed.set_author(url = member.avatar_url)
            embed.set_footer(text=f"Member ID: {member.id}")
            await logchannel.send(embed = embed)
        except HTTPException:
            return await logchannel.send(f"Member Banned:\n\nMember:{member.name}#{member.discriminator} ({member.id})")
    
    @commands.Cog.listener()
    async def on_command(self, command):
        database = await uttilities.connectdb(assets.Database_file)
        await database.execute(f"INSERT INTO commandlogs(userid, command) VALUES (?, ?)", (command.author.id, command.invoked_with,))
        await database.commit()
        try:
            await database.close()
        except ValueError:
            pass
def setup(bot):
    bot.add_cog(events(bot))