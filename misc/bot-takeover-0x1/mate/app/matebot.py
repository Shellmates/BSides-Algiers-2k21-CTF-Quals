#!/usr/bin/env python3

import discord
from discord.ext import commands
from discord.ext.commands import dm_only
from discord.ext.commands import Bot
from discord.ext.tasks import loop
import os
import subprocess
from dotenv import load_dotenv
import bcrypt
from db_handlers import UserHandler, EntryHandler
import validators
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import socket
import time

load_dotenv()

# Constants

TOKEN  = os.getenv("DISCORD_TOKEN")
# minimum master password length
MIN_LENGTH = 7
# timeout in minutes for logging out an inactive user
INACTIVE_TIMEOUT = 15
# host and port of openssl server
HOST = os.getenv("SERVER_HOST")
PORT = int(os.getenv("SERVER_PORT"))
# characters not allowed in username and password
NOT_ALLOWED = ['\n']

# Global variables

# stores master passwords and last time active of logged in users (uid is the key)
users = dict()
# bot client
client = Bot(
    command_prefix=commands.when_mentioned_or('!'),
    description="Mate - The Password Manager Bot",
    help_command=commands.DefaultHelpCommand(
        no_category="Commands"
    )
)

# Helper functions

# hash and salt password
def hash(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)

# checks if password is valid
def valid_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# parse openssl message
def parse_message(msg):
    data = json.loads(msg)
    if "parse_error" in data:
        raise ServerError(data["parse_error"])

    if "error" in data:
        return None, data["error"]

    return data["data"], None

# run a routine in a separate thread
async def runthread(routine, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(ThreadPoolExecutor(), routine, *args)

# send command to openssl server
# action is either "encrypt" or "decrypt"
def openssl_command(action, data, password):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(json.dumps({
            "action": action,
            "data": data,
            "password": password
        }).encode() + b'\n')
        recv_data = s.recv(2048)

    return parse_message(recv_data)

# wrapper to encrypt data with password
async def encrypt(data, password):
    return await runthread(openssl_command, "encrypt", data, password)

# wrapper to decrypt data with password
async def decrypt(data, password):
    return await runthread(openssl_command, "decrypt", data, password)

# get master password of user
def get_password(uid):
    if users.get(uid):
        return users.get("masterpass")
    return None

# Exceptions

# for authentification failures
class AuthFailure(commands.errors.CheckFailure):
    pass

# for encryption/decryption errors
class EncryptionError(commands.errors.CommandError):
    pass

# for openssl server errors
class ServerError(commands.errors.CommandError):
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
        name=":warning: DISCLAIMER",
        value="DO NOT use any of your real credentials (This disclaimer is not part of the challenge)",
        inline=False
    ).add_field(
        name=":information_source: Usage",
        value="Do !help in a DM for usage",
        inline=False
    ).set_thumbnail(url=f"{client.user.avatar_url}")

    await ctx.send(embed=embed)

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
        users[ctx.author.id] = {
            "masterpass": masterpass
        }
        await ctx.send(":white_check_mark: Login successful")
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

    registered = UserHandler.add(ctx.author.id, ctx.author.name, hash(masterpass))
    if registered :
        await ctx.send(":white_check_mark: Registration successful")
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
    await ctx.send(":white_check_mark: Logout successful")

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
                raise EncryptionError(err)
            password, err = await decrypt(data["password"], masterpass)
            if err:
                raise EncryptionError(err)

            await ctx.send(embed=discord.Embed(
                title=f":white_check_mark: {url}",
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
            await ctx.send(f":x: No credentials found for <{url}>")
    else: # get all entries
        data = EntryHandler.getall(ctx.author.id)
        if len(data) > 0 :
            for d in data :
                username, err = await decrypt(d["username"], masterpass)
                if err:
                    raise EncryptionError(err)
                password, err = await decrypt(d["password"], masterpass)
                if err:
                    raise EncryptionError(err)

                await ctx.send(embed=discord.Embed(
                    title=f":white_check_mark: {d['url']}",
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
            await ctx.send(":x: No credentials stored")

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
    if any(char in username or char in password for char in NOT_ALLOWED):
        await ctx.send(":x: Character not allowed")
        return
    if not validators.url(url):
        await ctx.send(":x: Not a valid URL")
        return

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
        await ctx.send(f":white_check_mark: Credentials added for <{url}>")
    else:
        await ctx.send(":x: Entry already exists")

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
    if any(char in username or char in password for char in NOT_ALLOWED):
        await ctx.send(":x: Character not allowed")
        return

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
        await ctx.send(f":white_check_mark: Credentials updated for <{url}>")
    else:
        await ctx.send(":x: Entry doesn't exist")

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
        await ctx.send(f":white_check_mark: Credentials deleted for <{url}>")
    else:
        await ctx.send(":x: This URL doesn't exist")

# Loops for background tasks

# logout inactive users after timeout
@loop(minutes=INACTIVE_TIMEOUT)
async def logout_inactive():
    for uid in list(users):
        if time.time() - users[uid]["lastactive"] > INACTIVE_TIMEOUT:
            users.pop(uid)
            await client.get_user(uid).send(":timer: Logged out due to inactivity")

# Events

@client.event
async def on_ready():
    for guild in client.guilds:
        print(f"[+] {client.user} connected to {guild}")
    await client.change_presence(activity=discord.Game(name="!mate"))

@client.listen("on_message")
async def update_lastactive(message):
    uid = message.author.id
    if not isinstance(message.channel, discord.DMChannel):
        return
    if uid not in users:
        return

    users[uid]["lastactive"] = time.time()

@client.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.errors.CommandNotFound):
        return
    elif isinstance(err, commands.errors.MissingRequiredArgument):
        await ctx.send(f":x: Missing a required argument. Do !help {ctx.command}")
    elif isinstance(err, commands.errors.BadArgument):
        await ctx.send(f":x: Bad argument. Do !help {ctx.command}")
    elif isinstance(err, commands.errors.ExpectedClosingQuoteError):
        await ctx.send(f":x: {err}")
    elif isinstance(err, commands.errors.UnexpectedQuoteError):
        await ctx.send(f":x: {err}")
    elif isinstance(err, commands.errors.InvalidEndOfQuotedStringError):
        await ctx.send(f":x: {err}")
    elif isinstance(err, commands.errors.PrivateMessageOnly):
        embed = discord.Embed(
            title=":lock: DMs only",
            description="This service is only available in direct messages",
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(err, AuthFailure):
        embed = discord.Embed(
            title=":x: Authentification failure",
            description=str(err),
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(err, EncryptionError):
        embed = discord.Embed(
            title=":x: Encryption Error",
            description=str(err),
            colour=discord.Colour.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(err, ServerError):
        print("Openssl Server error !")
        print("Error message:", err)
        await ctx.send(":x: Error")
    else:
        print("Uncaught error !")
        print("Error type:", type(err))
        print("Error message:", err)
        await ctx.send(":x: Error")

if __name__ == "__main__":
    logout_inactive.start()
    client.run(TOKEN)
