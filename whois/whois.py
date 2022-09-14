from http.client import FORBIDDEN, HTTPException
from types import NoneType
import discord
from discord.ext import commands 
import platform
import uttilities
import assets
#https://notify.run/c/hJcDZ5hSKND2sc2JVav3
from notify_run import Notify

notifer = Notify()
class whois(commands.Cog):
    def __init__(self, bot):
        """User information"""
        self.bot = bot

    @commands.command(name='av', aliases=['AV', 'Av', 'PFP', 'Pfp', 'pfp'])
    @commands.has_permissions(add_reactions=True)
    async def av(self, ctx, user: discord.Member = None):
        """Show the avatar of an user. Format: av @user"""
        if user != None:
            await ctx.send(user.avatar_url)
        else:
            await ctx.send(ctx.author.avatar_url)
    
    @commands.command(name='mydata')
    async def mydata(self, ctx):
        """See your data we collected from you. (MUST HAVE DMS OPEN)"""
        database = await uttilities.connectdb(assets.Database_file)
        embed = discord.Embed(name='Your data', color = discord.Color.blue())

        # Sanity check for modlogs
        logfinder = await database.execute(f"SELECT * FROM moderationLogs WHERE userid = {ctx.author.id}")
        logresult = await logfinder.fetchall()
        if logresult:
            embed.add_field(name='Total Moderation cases accross all servers', value=len(logresult), inline=False)
        else:
            embed.add_field(name="Total Moderation cases accross all servers:", value="0", inline=False)
        
        #Sanity check for bot admin:
        botadmin_finder = await database.execute(f"SELECT * FROM botdevs WHERE userid = {ctx.author.id}")
        botadmin_finder_result = await botadmin_finder.fetchall()
        if botadmin_finder_result:
            embed.add_field(name="Is bot admin:", value="True", inline=False)
        else:
            embed.add_field(name="Is bot admin:", value="False", inline=False)
        
        # Sanity check for commands:
        command_check = await database.execute(f"SELECT * from commandlogs WHERE userid = {ctx.author.id}")
        command_check_result = await command_check.fetchall()
        if command_check_result:
            embed.add_field(name="Commands issued", value=len(command_check_result), inline=False)
        else:
            embed.add_field(name="Commands issued:", value="None")
        
        try:
            embed.set_image(url=ctx.author.avatar_url)
            embed.set_footer(text= f"Author ID: {ctx.author.id}")
            await ctx.author.send(embed=embed)
            await Notify.send(message=f"{ctx.author.name}#{ctx.author.discriminator} Requested their data.\nTask completed succesfully.")
        except HTTPException:
            return await ctx.send(f"Sorry I am unable to retrieve your data")
        except discord.errors.Forbidden:
            return await ctx.reply("I am unable to dm you. Please open dms from this server.")
    
    @commands.command()
    @commands.has_permissions(add_reactions=True)
    async def bstats(self, ctx):
        """Command to check a few bot statistics."""
        python_version = platform.python_version()
        discord_py_version = discord.__version__
        total_guilds = len(self.bot.guilds)
        total_members = len(set(self.bot.get_all_members()))
        embed = discord.Embed(name='Bot stats', color=discord.Color.blue())
        embed.set_author(name='C-OPS bot')
        embed.add_field(name='**Python Version:**', value=python_version, inline=False)
        embed.add_field(name='**Library Version:**', value=discord_py_version, inline=False)
        embed.add_field(name='**Server Count:**', value=str(total_guilds), inline=False)
        embed.add_field(name='**Total Members:**', value=str(total_members), inline=False)
        embed.add_field(name="**Bot Version:**", value=uttilities.bot_version, inline=False)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def whois(self, ctx, *, user: discord.Member = None):
        """Check to see who this person is, their roles and other stuff. format: whois @user"""
        if user is None:
            user = ctx.author
        date_format = "%a, %d %b %Y %I:%M %p"
        embed = discord.Embed(color=discord.Color.orange(), description=user.mention)
        embed.set_author(name=str(user), icon_url=user.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Joined", value=user.joined_at.strftime(date_format))
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
        embed.add_field(name="Join position", value=str(members.index(user) + 1))
        embed.add_field(name="Registered", value=user.created_at.strftime(date_format))

        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            embed.add_field(name="Roles [{}]".format(len(user.roles) - 1), value=role_string, inline=False)
            embed.set_footer(text='ID: ' + str(user.id))
            return await ctx.send(embed=embed)
        else:
            embed.add_field(name="Roles:", value="None")
        return await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(whois(bot))