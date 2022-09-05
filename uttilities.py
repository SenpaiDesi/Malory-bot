import json
from enum import Enum
import aiosqlite
import discord
from discord.ext import commands
import assets
import sqlite3
import uttilities
main_config = ""
guilds = ""
bot_version = "0.0.1"

# json keys
key_config_token = "token"
key_config_dev_token = "devtoken"
key_config_developers = "developers"
key_guilds = "guilds"
key_guild_id = "id"
key_guild_prefix = "prefix"
key_guild_admin_roles = "admin_roles"


class EmbedColor(Enum):
    blue = discord.Color.blue()
    dark_blue = discord.Color.dark_blue()
    green = discord.Color.green()
    orange = discord.Color.orange()

def get_json(path):
    with open(path, "r") as f:
        return json.load(f)


def write_json(path, content):
    with open(path, "w") as f:
        json.dump(content, f, indent=4)



def get_token(dev_mode):
    if dev_mode:
        print("Run bot in dev mode...\n")
        return get_json(assets.config_path)["token"]
    else:
        print("Run bot live...\n")
        return main_config[key_config_token]

        
def get_guild(guild_id):
    for guild in guilds[key_guilds]:
        if guild[key_guild_id] == str(guild_id):
            return guild
            
def is_bot_admin():
    async def predicate(ctx):
        if is_bot_developer(ctx.author.id):
            return True
    return commands.check(predicate)


def is_bot_developer(member_id):
    database = sqlite3.connect(assets.Database_file)
    try:
        listdevs = database.execute(f"SELECT * FROM botdevs WHERE userid = {member_id}")
        returndevs = listdevs.fetchall()
        if not returndevs:
            database.close()
            return False
        else:
            database.close()
            return True
    except ValueError:
        pass
        

async def get_prefix(_bot, message):
    for guild in _bot.guilds:
        db = await aiosqlite.connect("database.db")
        try:
            await db.execute("CREATE TABLE IF NOT EXISTS guilds (guildID INT PRIMARY KEY, prefix text)")
            await db.commit()
        except ValueError:
            pass
        async with db.execute("SELECT prefix FROM guilds WHERE guildID = ?", (guild.id,)) as cursor:
            async for entry in cursor:
                prefix = entry
                return prefix



def create_embed(title, color):
    """Creates a Discord embed and returns it (for potential additional modification)"""
    embed = discord.Embed(title=title, color=color)
    return embed


def embed_add_field(embed, title, content, inline=True):
    """Helper function to add an additional field to an embed"""
    embed.add_field(name=title, value=content, inline=inline)


def create_simple_embed(title, color, field_title, field_content):
    """Creates a simple embed with only 1 field"""
    embed = create_embed(title, color)
    embed_add_field(embed, field_title, field_content)
    return embed


async def on_guild_join(guild):
    database = await aiosqlite.connect("./database.db")
    try:
        await database.execute("INSERT OR IGNORE INTO guilds VALUES (?, ?)", (guild.id, "mal-"))
        await database.commit()
        await database.close()
    except ValueError:
        pass


async def connectdb(db_path):
    return await aiosqlite.connect(db_path)