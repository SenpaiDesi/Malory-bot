from itertools import cycle
from colorama import Fore
import discord
from discord.ext import commands, tasks

import assets
import uttilities as utilities

intents = discord.Intents.default()
intents.members = True
status = cycle(assets.statuses)

bot = commands.Bot(command_prefix=utilities.get_prefix, intents=intents)
bot.remove_command("help")
bot.remove_command("ping")

for extension in assets.extensions:
    print(f"Load extension: {extension}")
    bot.load_extension(extension)
    print(f"Success loading extension: {extension}\n")


# Starts the presence loop.
@tasks.loop(minutes=3)
async def change_status():
    global status
    # Setting the status cycle.
    status = cycle(assets.statuses)  # Creates statuses for the status cycle.
    await bot.change_presence(activity=discord.Game(next(status)))


# Sets the bot's basic prefix to * for any new server it joins. Can later be adjusted using the prefix command.
# Removes the prefix for that server when the bot gets removed, kicked or banned.
@bot.event
async def on_guild_join(_guild):
    for guild in bot.guilds:
        await utilities.on_guild_join(guild)


# Removes the prefix for that server when the bot gets removed, kicked or banned.
@bot.event
async def on_guild_remove(guild):
    database = await  utilities.connectdb(assets.Database_file)
    try:
        await database.execute(f"DELETE FROM guilds WHERE guildID = {guild.id}")
        await database.commit()
        await database.close()
    except ValueError:
        pass


@bot.event
# Logging in and selecting the first status for the status cycler to use.
async def on_ready():
    # sanity check, in case the bot was added during downtime
    for guild in bot.guilds:
        await utilities.on_guild_join(guild)

    change_status.start()
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(status))



# PREFIX COMMAND(S)
# Changes the prefix of that server for the bot. Applied to prefixes.json [Can be done better I know.]
@bot.command(name="prefix")
@commands.has_permissions(add_reactions=True)
async def prefix(ctx, _prefix=None):
    database = await utilities.connectdb(assets.Database_file)
    """Change your prefix."""
    if _prefix is not None:
        try:
            string_prefix = str(_prefix)
            await database.execute(f"DELETE FROM guilds WHERE guildID = {ctx.guild.id}")
            await database.commit()
            await database.execute(f"INSERT INTO guilds VALUES ({ctx.guild.id}, '{string_prefix}')")
            await database.commit()
            await database.close()
        except ValueError:
            pass
        await ctx.send(embed=utilities.create_simple_embed("Prefix", utilities.EmbedColor.blue.value, "Prefix set!", f"Success! This guild's prefix is now {_prefix}"))
    else:
        # no need to load json, as this command was called with the adequate prefix
        await ctx.send(embed=utilities.create_simple_embed("Current prefix", utilities.EmbedColor.blue.value, "Your current prefix is: ", ctx.prefix))


@bot.command(name="logout", aliases=["SHD", "shd"], hidden=True)
async def logout(ctx):
    if not utilities.is_bot_developer(ctx.author.id):
        return

    await ctx.send("Shut down")
    change_status.cancel()
    try:
        await bot.close()
    except ConnectionError:
        pass
    print("Bot shutdown.")



def run(dev_mode):
    print("Bot running")
    bot.run(utilities.get_token(dev_mode))