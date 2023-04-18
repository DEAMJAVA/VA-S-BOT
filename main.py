current_version = 'V2.0'

import discord
import json
import os
import tkinter as tk
import youtube_dl
import requests
import numpy as np
import tensorflow as tf
import io
import openai

from PIL import Image
from github import Github
from discord import Status
from tkinter import messagebox
from discord.ext import commands
from discord.utils import get
from youtube_search import YoutubeSearch
from io import BytesIO

# Load or save bot configuration from BotConfig.json file

if not os.path.isfile('BotConfig.json'):
    print('No config file found creating BotConfig.json')
    INPUT_PREFIX= input('\nWhat do you want the bot prefix to be \n')
    INPUT_BOT_TOKEN= input('\nEnter bot token \n')
    INPUT_WELCOME_CHANNEL_ID= input('\nEnter welcome channel ID \n')
    INPUT_OWNER_ID= input("\nEnter owner's ID\n")
    INPUT_OWNER_NAME= input("\nEnter owner's name\n")
    INPUT_MOD_ROLE_NAME= input("\nEnter MOD role name\n")
    INPUT_OWNER_ROLE_NAME= input("\nEnter owner role name\n")
    config = {
        'prefix': INPUT_PREFIX,
        'bot_token': INPUT_BOT_TOKEN,
        'welcome_channel': INPUT_WELCOME_CHANNEL_ID,
        'owner_id': INPUT_OWNER_ID,
        'owner_name': INPUT_OWNER_NAME,
        'mod_role': INPUT_MOD_ROLE_NAME,
        'owner_role': INPUT_OWNER_ROLE_NAME,
        'imagine_enabled': 'False'
    }
    with open('BotConfig.json', 'w') as f:
        f.write(json.dumps(config, indent=4, ensure_ascii=False, separators=(',', ': ')) + '\n')
    messagebox.showinfo(title="Va's BOT", message="Please restart the app", icon=messagebox.INFO)
else:

    with open('BotConfig.json') as f:
        config = json.load(f)

    bot = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all())
    # Suppress noise about console usage from errors
    youtube_dl.utils.bug_reports_message = lambda: ''

    # Suppress noise about too many arguments to function
    youtube_dl.YoutubeDL.extract_info = lambda ydl, url, download=None: ydl.extract_info(url, download=False)

    def has_required_perm():
        async def predicate(ctx):
            required_role_name = config['mod_role'] 
            required_role = discord.utils.get(ctx.guild.roles, name=required_role_name)

            if required_role not in ctx.author.roles:
                await ctx.send("You don't have the required permision to execute this command!")
                return False

            return True

        return commands.check(predicate)




    def has_owner_perm():
        async def predicate(ctx):
            required_role_name = config['owner_role'] 
            required_role = discord.utils.get(ctx.guild.roles, name=required_role_name)

            if required_role not in ctx.author.roles:
                await ctx.send("You don't have the required permision to execute this command!")
                return False

            return True

        return commands.check(predicate)

    # Setup bot events
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')

    @bot.event
    async def on_member_join(member):
        channel = bot.get_channel(config['welcome_channel'])
        await channel.send(f'Welcome to the server, {member.mention}!')

    # Define bot commands
    @bot.command()
    @has_required_perm()
    async def kick(ctx, member: discord.Member):
        try:
            await member.kick()
            await ctx.send(f"{member.name} has been kicked!")
        except Exception as e:
            await ctx.send(f'An error occured: {e}')

    @bot.command()
    @has_required_perm()
    async def ban(ctx, member: discord.Member):
        try:
            await member.ban()
            await ctx.send(f'{member} has been banned from the server.)')
        except Exception as e:
            await ctx.send(f'An error occured: {e}')

    @bot.command()
    @has_required_perm()
    async def unban(ctx, *, member):
        try:
            banned_users = await ctx.guild.bans()
            member_name, member_discriminator = member.split('#')

            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await ctx.guild.unban(user)
                    await ctx.send(f'{user.mention} has been unbanned from the server.')
                    return

            await ctx.send(f'Could not find banned user: {member}')
        except Exception as e:
            await ctx.send(f'An error occured: {e}')

    @bot.command()
    @has_required_perm()
    async def mute(ctx, member: discord.Member):
        try:
            muted_role_name = 'Muted'
            muted_role = discord.utils.get(ctx.guild.roles, name=muted_role_name)

            if muted_role is None:
                # Create the muted role if it doesn't exist
                muted_role = await ctx.guild.create_role(name=muted_role_name)

                for channel in ctx.guild.channels:
                    # Deny send messages permission to the muted role for all channels
                    await channel.set_permissions(muted_role, send_messages=False)

                # Add the muted role to the member
                await member.add_roles(muted_role)
                await ctx.send(f'{member.mention} has been muted.')
        except Exception as e:
            await ctx.send(f'An error occured: {e}')
    @bot.command()
    @has_owner_perm()
    async def shutdown(ctx):
        try:
            await ctx.send('Shutting down...')
            exit()
        except:
            exit()

    @bot.command()
    @has_required_perm()
    async def status(ctx, arg: str):
        try:
            if arg == 'online':
                await bot.change_presence(status=Status.online)
                await ctx.send("Status set to online.")
            elif arg == 'invisible':
                await bot.change_presence(status=Status.invisible)
                await ctx.send("Status set to invisible.")
            elif arg == 'idle':
                await bot.change_presence(status=Status.idle)
                await ctx.send("Status set to idle.")
            elif arg == 'dnd':
                await bot.change_presence(status=Status.dnd)
                await ctx.send("Status set to dnd.")
            else:
                await ctx.send("Invalid status provided. Please choose from 'online', 'invisible', 'idle', or 'dnd'.")
        except Exception as e:
            await ctx.send(f'An error occured: {e}')
    @bot.command()
    @commands.has_role(config['owner_role'])
    async def set_status(ctx, status_type: str, *, status_text: str):
        try:
            """Set the bot's status"""
            if status_type.lower() == "playing":
                activity = discord.Game(name=status_text)
            elif status_type.lower() == "listening":
                activity = discord.Activity(type=discord.ActivityType.listening, name=status_text)
            elif status_type.lower() == "watching":
                activity = discord.Activity(type=discord.ActivityType.watching, name=status_text)
            else:
                await ctx.send("Invalid status type. Valid options are `playing`, `listening`, `watching`, and `streaming`.")
                return

            await bot.change_presence(activity=activity)
            await ctx.send(f"Status set to: {status_type.title()} {status_text}")
        except Exception as e:
            await ctx.send(f'An error occured: {e}')
    @bot.command()
    @commands.has_role(config['owner_role'])
    async def clear_status(ctx):
        try:
            """Clear the bot's status"""
            await bot.change_presence(activity=None)
            await ctx.send("Status cleared.")
        except Exception as e:
            await ctx.send('An error occured: {e}')
    @bot.command()
    @has_required_perm()
    async def setnickname(ctx, member: discord.Member, *, new_nickname: str):
        try:
            await member.edit(nick=new_nickname)
            await ctx.send(f"Nickname has been changed to {new_nickname}.")
        except Exception as e:
            await ctx.send(f'An error occured: {e}')
    @bot.command()
    async def nickname(ctx, *, new_name: str):
        try:
            await ctx.guild.me.edit(nick=new_name)
            await ctx.send(f"My nickname has been changed to {new_name}")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    @bot.command()
    async def imagine(ctx, keyword=None):
        if config['imagine_enabled'] == True:
            try:
                 if not keyword:
                    await ctx.send('Please provide a keyword to imagine!')
                    return
                 image_url = get_random_image(keyword)
                 await ctx.send(f'Here is an image of {keyword} that I imagined:\n{image_url}')
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")
        else:
            await ctx.send("Sorry, the imagine command is currently disabled.")

    @bot.command()
    @commands.has_role(config['owner_role'])
    async def enable_imagine(ctx):
        config['imagine_enabled'] = True
        with open('BotConfig.json', 'w') as f:
            json.dump(config, f)
        await ctx.send("The imagine command has been enabled.")

    @bot.command()
    @commands.has_role(config['owner_role'])
    async def disable_imagine(ctx):
        config['imagine_enabled'] = False
        with open('config.json', 'w') as f:
            json.dump(config, f)
        await ctx.send("The imagine command has been disabled.")



    openai.api_key = "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"
    

    @bot.command()
    async def gen(ctx, *, text):
        response = openai.Completion.create(
            prompt=text,
            num_images=1,
            size="256x256",
            response_format="url"
        )
        image_url = response.choices[0].text
        embed = discord.Embed()
        embed.set_image(url=image_url)

        await ctx.send(embed=embed)














    # Define help command
    @bot.command()
    async def h(ctx):
        
        prefix=config['prefix']
        owner_id=config['owner_id']
        owner = await bot.fetch_user(owner_id)
        help_msg =(f'''**Commands:**
        `kick <member>` - Kick a member from the server.
        `ban <member>` - Ban a member from the server.
        `unban <member>` - Unban a member from the server.
        `mute <member>` - Mute a member in the server.
        `shutdown` - Shut down the bot.
        `h` - Show this help message.
        `set_status <value>` - sets custom status.
        `clear_status` - Sets to default status
        `setnickname <member>` - Changes nickname of other members
        `nickname <name>` - Sets custom nickname 
        And add "''' + prefix + '" Before any of the commands Example "' + prefix +
        """h" """ + f"""For More Info Contact <@{owner.id}>""")

        await ctx.send(help_msg)






    # Set your Github access token as an environment variable
    ACCESS_TOKEN = os.environ.get('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')
    # Set the repository name and owner
    REPO_NAME = 'VA-S-BOT'
    REPO_OWNER = 'DEAMJAVA'

    def check_for_updates():
        # Authenticate with Github using your access token
        g = Github(ACCESS_TOKEN)
        repo = g.get_repo(f'{REPO_OWNER}/{REPO_NAME}')
        
        # Get the latest release from the releases tag
        latest_release = repo.get_latest_release()
        
        # Compare the latest release version with the current version
        m = f"New version {latest_release.tag_name} available! \nDownload URL: {latest_release.html_url}"
        
        if latest_release.tag_name >= current_version:
            print(f'New version {latest_release.tag_name} available!')
            print(f'Download URL: {latest_release.html_url}')
            messagebox.showinfo(title="Va's BOT", message=m, icon=messagebox.INFO)



    check_for_updates()    

    # Start the bot
    bot.run(config['bot_token'])
