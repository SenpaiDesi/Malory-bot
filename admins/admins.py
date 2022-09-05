from sqlite3 import IntegrityError
import uttilities as utilities
from discord.ext import commands
from errors import DatabaseError
import discord
import assets

bot_shutting_down = "Bot shutting down..."
no_permission = "You do not have permission for this command."
process = "Starting task {}/2"


class admins(commands.Cog):
    """Admin only commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="listguilds", hidden=True)
    @utilities.is_bot_admin()
    async def listguilds(self, ctx):
        for guild in self.bot.guilds:
            await ctx.send(f"Server Name: {guild.name}\nID: {guild.id}")

    @commands.command(name="load", hidden=True)
    @utilities.is_bot_admin()
    async def load(self, ctx, _module):
        if not utilities.is_bot_developer(ctx.author.id):
            return

        try:
            self.bot.load_extension(_module)
        except Exception as e:
            await ctx.send(f"{type(e).__name__} - {e}")
        else:
            await ctx.send(f"Loaded `{_module}`")

    @commands.command(name="unload", hidden=True)
    async def unload(self, ctx, _module):
        if not utilities.is_bot_developer(ctx.author.id):
            return

        try:
            self.bot.unload_extension(_module)
        except Exception as e:
            await ctx.send(f"{type(e).__name__} - {e}")
        else:
            await ctx.send(f"Unloaded `{_module}` ")

    @commands.command(name="reload", hidden=True)
    async def _reload(self, ctx, _module):
        if not utilities.is_bot_developer(ctx.author.id):
            return

        try:
            self.bot.unload_extension(_module)
            self.bot.load_extension(_module)
        except Exception as e:
            await ctx.send(f"{type(e).__name__} - {e}")
        else:
            await ctx.send(f"Reloaded `{_module}`")

    @commands.command(name="listadmins", hidden=True)
    async def list_admins(self, ctx):
        database = await utilities.connectdb("./database.db")
        if not utilities.is_bot_developer(ctx.author.id):
            return
        message = "Bot Admins:\n"
        async with database.execute("SELECT userid, name FROM botdevs") as cursor:
            async for entry in cursor:
                userid, username = entry
                message += f"Dev ID: {userid} -- Dev Name: {username}\n"

        await ctx.send(message)
        try:
            await database.close()
        except ValueError:
            pass

    @commands.command(hidden=True)
    @utilities.is_bot_admin()
    async def dbsetup(self, ctx):
        database = await utilities.connectdb("./database.db")
        message = await ctx.send(process.format("1"))
        try:
            await database.execute("CREATE TABLE IF NOT EXISTS guilds (guildID INTEGER PRIMARY KEY, prefix TEXT)")
            await database.commit()
            await database.execute("CREATE TABLE IF NOT EXISTS moderationLogs (logid INTEGER PRIMARY KEY, guildid INTEGER, moderationLogType INTEGER, userid INTEGER, moduserid INTEGER, content VARCHAR, duration INTEGER)")
            await database.commit()
            await database.execute("CREATE TABLE IF NOT EXISTS logtypes (ID INTEGER PRIMARY KEY, type TEXT)")
            await database.commit()
            await database.execute("CREATE TABLE IF NOT EXISTS botdevs (userid INTEGER PRIMARY KEY, name TEXT)")
            await database.commit()
            await message.edit(content = process.format("2"))
        except Exception as e:
            return await ctx.send(f"Could not complete task 1 because of \n{e}")
        
        try:
            await database.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (1, "warn",))
            await database.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (2, "mute",))
            await database.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (3, "unmute",))
            await database.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (4, "kick",))
            await database.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (5, "softban",))
            await database.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (6, "ban",))
            await database.execute("INSERT OR IGNORE INTO logtypes VALUES (?, ?)", (7, "unban",))
            await database.commit()
        except Exception as e:
            return await ctx.send(f"Could not complete task 2 because of \n{e}")
        try:
            await database.close()
            await message.edit(content="Done!")
        except ValueError:
            pass
    
    @commands.command(name='botadmins')
    @utilities.is_bot_admin()
    async def modify_bot_admins(self, ctx, action, userid):
        database = await utilities.connectdb(assets.Database_file)
        user = await self.bot.fetch_user(userid)
        string_member_name = str(user.name)
        
        if action == "add":
            try:
                try:
                    await database.execute("INSERT INTO botdevs VALUES (?, ?)", (user.id, string_member_name))
                except IntegrityError:
                    return await ctx.send(DatabaseError.duplicate_bot_dev_entry) 
                await database.commit()
                embed = utilities.create_simple_embed(title="✅Success", color=utilities.EmbedColor.blue.value, field_title=f"Completed {action}", field_content=f"Completed {action} on {user.id}")
                await ctx.send(embed = embed)
                await database.close()
            except ValueError:
                pass
        elif action == "delete" or "remove":
            try:
                await database.execute(f"DELETE FROM botdevs WHERE userid = {user.id} ")
                await database.commit()
                embed = utilities.create_simple_embed(title="✅Success", color=utilities.EmbedColor.blue.value, field_title=f"Completed {action}", field_content=f"Completed {action} on {user.id}")
                await ctx.send(embed = embed)
                await database.close()
            except ValueError:
                pass
def setup(bot):
    bot.add_cog(admins(bot))