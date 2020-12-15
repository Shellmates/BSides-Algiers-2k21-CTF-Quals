#!/usr/bin/python3 

import discord
from discord.ext import commands
from discord.ext.commands import dm_only
import os
import subprocess
from dotenv import  load_dotenv
import bcrypt
from db_handlers import UserHandler, EntryHandler
import validators

load_dotenv()

# Constants

TOKEN  = os.getenv('DISCORD_TOKEN')
# minimum master password length
MIN_LENGTH = 7

# Global variables

# stores master passwords of logged in users (uid is the key)
users = dict()
# activity message
activity = discord.Game(name="!mate")
# bot client
client = commands.Bot(
    command_prefix=commands.when_mentioned_or('!'),
    description="Mate - The Password Manager Bot",
    help_command=commands.DefaultHelpCommand(
        no_category="Commands"
    )
)

# Helper functions

def hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

def valid_password(masterpass, hashed):
    return bcrypt.checkpw(masterpass.encode(), hashed)

# encrypt data using password
# returns encrypted data
# on error, returns None and error message
async def encrypt(data, password):
    cmd = "echo -n '{}' | openssl enc -aes-256-cbc -pbkdf2 -pass pass:'{}' -a".format(data, password)
    print("encrypt cmd:", cmd)
    with subprocess.Popen(cmd, shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        out, err = map(bytes.decode, p.communicate())
        exit_code = p.wait()
        if exit_code != 0:
            return None, err.rstrip()
    return out.rstrip(), None

# decrypt data using password
# on error, returns error message and False indicating failure
async def decrypt(data, password):
    cmd = "echo -n '{}' | base64 -d | openssl enc -aes-256-cbc -pbkdf2 -pass pass:'{}' -d".format(data, password)
    print("decrypt cmd:", cmd)
    with subprocess.Popen(cmd, shell=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
        out, err = map(bytes.decode, p.communicate())
        exit_code = p.wait()
        if exit_code != 0:
            return None, err.rstrip()
    return out.rstrip(), None

def get_password(uid):
    return users.get(uid)

# Exceptions

class AuthFailure(commands.errors.CheckFailure):
    pass

class EncryptionError(commands.errors.CommandError):
    pass

class DecryptionError(commands.errors.CommandError):
    pass

# Check decorators

# checks whether user is logged in
def logged_in():
    def predicate(ctx):
        if ctx.author.id not in users:
            raise AuthFailure("Not logged in")
        return True
    return commands.check(predicate)

# checks whether user is logged out
def logged_out():
    def predicate(ctx):
        if ctx.author.id in users:
            raise AuthFailure("Already logged in")
        return True
    return commands.check(predicate)

# Commands

@client.command(name="mate", help="Bot description")
async def mate(ctx):
    embed = discord.Embed(
        title="Mate - The Password Manager Bot",
        description='''\
This is Mate, a very secure password manager that you can rely on.
You can store an endless amount of credentials for FREE!
You don't risk losing your precious data thanks to OPENSSL, the latest encryption technology.
Use our app now by DMing the bot and free yourself from the pain of remembering all your complex passwords.''',
        colour=discord.Colour.teal()
    ).add_field(
        name="DISCLAIMER",
        value="DO NOT use any of your real credentials (This disclaimer is not part of the challenge)",
        inline=False
    ).add_field(
        name="Usage",
        value="Do !help in a DM for usage",
        inline=False
    ).set_thumbnail(url=f"{client.user.avatar_url}")
    await ctx.send(embed=embed)
    print(f"msg: {ctx.message}")
    print(f"created at: {ctx.message.created_at}")

@client.command(
    name="login",
    help='''\
Login into your account.
Example: !login 1337password\
'''
)
@dm_only()
@logged_out()
async def login(ctx, masterpass: str):
    creds = UserHandler.get(ctx.author.id)
    if creds is None:
        raise AuthFailure("User doesn't exist! Register first")
    if valid_password(masterpass, creds["masterpass"]):
        users[ctx.author.id] = masterpass
        await ctx.send("Login successful")
    else:
        raise AuthFailure("Wrong credentials")

@client.command(
    name="register",
    help='''\
Register your account.
Example: !register 1337password\
'''
)
@dm_only()
@logged_out()
async def register(ctx, masterpass: str):
    if len(masterpass) < MIN_LENGTH:
        raise AuthFailure("Password is too short")  
    else:
        registered = UserHandler.add(ctx.author.id, ctx.author.name, hash(masterpass))
        if registered :
            await ctx.send("Registration successful")
            await login(ctx, masterpass)
        else:
            raise AuthFailure("User already registered")

@client.command(
    name="logout",
    help="Log out of your account"
)
@dm_only()
@logged_in()
async def logout(ctx):
    users.pop(ctx.author.id)
    await ctx.send("Logout successful")

@client.command(
    name="view",
    aliases=["v"],
    help='''\
View creds associated to URL (view all if no URL is provided)
Example: !view https://discord.com\
'''
)
@dm_only()
@logged_in()
async def view(ctx, url: str=None):
    masterpass = get_password(ctx.author.id)
    if url is not None:
        data = EntryHandler.get(ctx.author.id, url)
        if data is not None:
            username, err = await decrypt(data["username"], masterpass)
            if err:
                raise DecryptionError(err)
            password, err = await decrypt(data["password"], masterpass)
            if err:
                raise DecryptionError(err)

            await ctx.send(embed=discord.Embed(
                title=url,
                colour=discord.Colour.teal(),
            ).add_field(
                name="username",
                value=username,
                inline=False
            ).add_field(
                name="password",
                value=password,
                inline=False
            ))
        else:
            await ctx.send(f"No credentials found for <{url}>")
    else: # get all entries
        data = EntryHandler.getall(ctx.author.id)
        if len(data) > 0 :
            for d in data :
                username, err = await decrypt(d["username"], masterpass)
                if err:
                    raise DecryptionError(err)
                password, err = await decrypt(d["password"], masterpass)
                if err:
                    raise DecryptionError(err)

                await ctx.send(embed=discord.Embed(
                    title=d["url"],
                    colour=discord.Colour.teal(),
                ).add_field(
                    name="username",
                    value=username,
                    inline=False
                ).add_field(
                    name="password",
                    value=password,
                    inline=False
                ))
        else:
            await ctx.send("No credentials stored")

@client.command(
    name="add",
    aliases=["a"],
    help='''\
Add a new entry of credentials for specified URL
Example: !add https://discord.com coolUsername 1337password\
'''
)
@dm_only()
@logged_in()
async def add(ctx, url: str, username: str, password: str):
    if not validators.url(url):
        await ctx.send("Not a valid URL")
    else:
        masterpass = get_password(ctx.author.id)
        enc_username, err = await encrypt(username, masterpass)
        if err:
            raise EncryptionError(err)
        enc_password, err = await encrypt(password, masterpass)
        if err:
            raise EncryptionError(err)

        added = EntryHandler.add(
            ctx.author.id,
            url,
            enc_username,
            enc_password
        )
        if added:
            await ctx.send("Credentials added for <{}>".format(url))
        else:
            await ctx.send("Entry already exists")

@client.command(
    name="update",
    aliases=["u"],
    help='''\
Update credentials entry of specified URL
Example: !update https://discord.com coolerUsername 1337passwordl33t\
'''
)
@dm_only()
@logged_in()
async def update(ctx, url: str, username: str, password: str):
    masterpass = get_password(ctx.author.id)
    enc_username, err = await encrypt(username, masterpass)
    if err:
        raise EncryptionError(err)
    enc_password, err = await encrypt(password, masterpass)
    if err:
        raise EncryptionError(err)

    updated = EntryHandler.add(
        ctx.author.id,
        url,
        enc_username,
        enc_password
    )
    if updated:
        await ctx.send("Credentials updated for <{}>".format(url))
    else:
        await ctx.send("Entry doesn't exist")

@client.command(
    name="delete",
    aliases=["d"],
    help='''\
Delete entry specified by URL
Example: !delete https://discord.com\
'''
)
@dm_only()
@logged_in()
async def delete(ctx, url: str):
    deleted = EntryHandler.delete(ctx.author.id, url)
    if deleted:
        await ctx.send("Credentials deleted for <{}>".format(url))
    else:
        await ctx.send("This URL doesn't exist")

# Events

@client.event
async def on_ready():
    guild = client.guilds[0]
    print("[+] {} connected to {}".format(client.user, guild))
    await client.change_presence(activity=activity)

@client.event
async def on_command_error(ctx, err):
    description = None
    if isinstance(err, commands.errors.CommandNotFound):
        return
    elif isinstance(err, commands.errors.MissingRequiredArgument):
        await ctx.send(f"Missing a required argument. Do !help {ctx.command}")
    elif isinstance(err, commands.errors.BadArgument):
        await ctx.send(f"Bad argument. Do !help {ctx.command}")
    elif isinstance(err, commands.errors.ExpectedClosingQuoteError):
        await ctx.send(str(err))
    elif isinstance(err, commands.errors.UnexpectedQuoteError):
        await ctx.send(str(err))
    elif isinstance(err, commands.errors.PrivateMessageOnly):
        embed = discord.Embed(
            title="DMs only",
            description="This service is only available in direct messages",
            colour=discord.Colour.gold()
        )
        await ctx.send(embed=embed)
    elif isinstance(err, AuthFailure):
        embed = discord.Embed(
            title="Authentification failure",
            description=str(err),
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(err, EncryptionError):
        embed = discord.Embed(
            title="Encryption Error",
            description=str(err),
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(err, DecryptionError):
        embed = discord.Embed(
            title="Decryption Error",
            description=str(err),
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed)
    else:
        print("Uncaught error !")
        print("Error type:", type(err))
        print("Error message:", err)
        await ctx.send("Error")

if __name__ == "__main__":
    client.run(TOKEN)
