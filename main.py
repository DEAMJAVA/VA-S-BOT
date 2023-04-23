current_version = 'V4.0'

import discord
import json
import os
import tkinter as tk
import youtube_dl
import requests
import io
import openai
import random as rand

from github import Github
from discord import Status
from tkinter import messagebox
from discord.ext import commands
from discord.utils import get

# Load or save bot configuration from BotConfig.json file

if not os.path.isfile('BotConfig.json'):
    print('No config file found creating BotConfig.json')
    INPUT_PREFIX= input('\nWhat do you want the bot prefix to be \n')
    INPUT_BOT_TOKEN= input('\nEnter bot token \n')
    INPUT_WELCOME_CHANNEL_ID= input('\nEnter welcome channel ID \n')
    INPUT_OWNER_ID= input("\nEnter owner's ID\n")
    INPUT_OWNER_NAME= input("\nEnter owner's name\n")
    INPUT_OWNER_ROLE_NAME= input("\nEnter owner role name\n")
    INPUT_MOD_ROLE_NAME= input("\nEnter MOD role name\n")
    QUESTION = input("\nDoes your server have custom member role (YESY/NO)\n")
    if QUESTION.lower() == 'yes':
        INPUT_MEMBER_ROLE_NAME= input("\nEnter member role name\n")
    else:
        INPUT_MEMBER_ROLE_NAME= None
    config = {
        'prefix': INPUT_PREFIX,
        'bot_token': INPUT_BOT_TOKEN,
        'welcome_channel': INPUT_WELCOME_CHANNEL_ID,
        'owner_id': INPUT_OWNER_ID,
        'owner_name': INPUT_OWNER_NAME,
        'mod_role': INPUT_MOD_ROLE_NAME,
        'owner_role': INPUT_OWNER_ROLE_NAME,
        'member_role': INPUT_MEMBER_ROLE_NAME,
        'debug': 'False'
    }
    with open('BotConfig.json', 'w') as f:
        f.write(json.dumps(config, indent=4, ensure_ascii=False, separators=(',', ': ')) + '\n')
    messagebox.showinfo(title="Va's BOT", message="Please restart the app", icon=messagebox.INFO)
else:

    with open('BotConfig.json') as f:
        config = json.load(f)

    bot = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all())

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        debug = config['debug']
        print(f'Debug: {debug}')

    @bot.event
    async def on_member_join(member):
        ID = int(config['welcome_channel'])
        channel = bot.get_channel(1096103887188021248) # Replace channel_id with the ID of the channel you want the bot to send the message in
        await channel.send(f'Welcome to the server, {member.mention}!')
        if config['debug'] == True:
            print(ID)
            print(bot.get_all_channels())

    def has_required_perm():
        async def predicate(ctx):
            try:
                owner_role_name = config['owner_role']
                owner_role = discord.utils.get(ctx.guild.roles, name=owner_role_name)
                mod_role_name = config['mod_role']
                mod_role = discord.utils.get(ctx.guild.roles, name=mod_role_name)
                owner_id = config['owner_id']

                if config['debug'] == "True":
        

                    print(f'Author ID: {ctx.author.id}')
                    print(f'Owner ID: {owner_id}')

                    if owner_role not in ctx.author.roles:
                        y= 'No'
                    else:
                        y= 'Yes'

                    if mod_role not in ctx.author.roles:
                        my= 'No'
                    else:
                        my= 'Yes'        
            
                    author_name = ctx.author.name
                    print(f'does Author has Owner role: {y}')
                    print(f'does Author has Mod role: {my}')
                    print(f'Name: {author_name}')


                if str(owner_id) != str(ctx.author.id) and mod_role not in ctx.author.roles:
                    await ctx.send("You don't have the required permision to execute this command!")
                    return False
            except Exception as e:
                await ctx.send(f'An error occured: {e}')

            return True

        return commands.check(predicate)

    def has_owner_perm():
        async def predicate(ctx):
            owner_role_name = config['owner_role']
            owner_role = discord.utils.get(ctx.guild.roles, name=owner_role_name)
            mod_role_name = config['mod_role']
            mod_role = discord.utils.get(ctx.guild.roles, name=mod_role_name)
            owner_id = config['owner_id']

            if config['debug'] == "True":
        

                print(f'Author ID: {ctx.author.id}')
                print(f'Owner ID: {owner_id}')

                if owner_role not in ctx.author.roles:
                    y= 'No'
                else:
                    y= 'Yes'

                if mod_role not in ctx.author.roles:
                    my= 'No'
                else:
                    my= 'Yes'        
        
                author_name = ctx.author.name

                print(f'does Author has Owner role: {y}')
                print(f'does Author has Mod role: {my}')
                print(f'Name: {author_name}')

            if str(owner_id) != str(ctx.author.id) and owner_role not in ctx.author.roles:
                    await ctx.send("You don't have the required permission to execute this command!")
                    return False
            return True


        return commands.check(predicate)
    @bot.command()
    async def about_me(ctx):
        try:
            role_names = [role.name for role in ctx.author.roles]
            roles = role_names
            Id = ctx.author.id
            name=ctx.author.name
            message = (f'''
            roles: {roles}
            ID: {Id}
            Name: {name}''')
            await ctx.send(message)
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

        
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
            await ctx.send(f'{member} has been banned from the server.')
        except Exception as e:
            await ctx.send(f'An error occured: {e}')

    @bot.command()
    @has_required_perm()
    async def unban(ctx, *, name):
        try:
            async for ban_entry in ctx.guild.bans():
                user = ban_entry.user
                if user.name.lower() == name.lower():
                    await ctx.guild.unban(user)
                    await ctx.send(f'{user.mention} has been unbanned from the server.')
                    return
            await ctx.send(f'Could not find banned user: {name}')
        except Exception as e:
            await ctx.send(f'An error occurred: {e}')






    @bot.command()
    @has_required_perm()
    async def mute(ctx, member: discord.Member, *, reason=None):
        guild = ctx.guild
        try:
            # Create a mute role if it doesn't already exist
            mute_role = discord.utils.get(guild.roles, name="Muted")
            if not mute_role:
                permissions = discord.Permissions(send_messages=False, speak=False)
                mute_role = await guild.create_role(name="Muted", permissions=permissions)
                
                # Set permissions for all channels
                for channel in guild.channels:
                    await channel.set_permissions(mute_role, send_messages=False, speak=False)    
            # Add the mute role to the member and send a message
            await member.add_roles(mute_role, reason=reason)
            await ctx.send(f"{member.mention} has been muted.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @bot.command()
    @has_required_perm()
    async def unmute(ctx, member: discord.Member, *, reason=None):
        guild = ctx.guild
        try:
            muted_role = discord.utils.get(guild.roles, name='Muted')
            await member.remove_roles(muted_role)
            await ctx.send(f"{member.mention} has been unmuted.")
        except Exception as e:
            await ctx.send(f'An error occured: {e}')

        
    @bot.command()
    @has_owner_perm()
    async def shutdown(ctx):
        try:
            await ctx.send('Shutting down...')
            return
        except:
            return

    @bot.command()
    @has_owner_perm()
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
    @has_required_perm()
    async def nickname(ctx, *, new_name: str):
        try:
            await ctx.guild.me.edit(nick=new_name)
            await ctx.send(f"My nickname has been changed to {new_name}")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

        
    @bot.command()
    async def ticket(ctx):
        guild = ctx.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category(name="Tickets")
        role = discord.utils.get(ctx.guild.roles, name=config['member_role'])
        if config['member_role'] == None:
            role= guild.default_role 
        mod_role = discord.utils.get(ctx.guild.roles, name=config['mod_role'])

        overwrites = {
            role: discord.PermissionOverwrite(read_messages=False),
            mod_role : discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        debug = config['debug']
        if debug == "True":
            print(f'Default role: {role}')
            print(f'Mod role: {mod_role}')

        channel = await category.create_text_channel(f'ticket-{ctx.author.display_name}', overwrites=overwrites)
        msg = (f"""
       Your ticket has been created at {channel.mention}.
       A staff will help you shortly""")
        await ctx.send(msg)

    @bot.command()
    @has_required_perm()
    async def close(ctx):
        try:
            if not ctx.channel.name.startswith('ticket-'):
                await ctx.send('This command can only be used in a ticket channel.')
                return
            await ctx.channel.delete()
        except Exception as e:
            print(f"An error occurred: {e}")
            
    @bot.command()
    async def random(ctx, mi=None, ma=None):
        try:
            prefix = config['prefix']
            if mi == None or ma == None or int(mi) >= int(ma) or not isinstance(int(mi), int) or not isinstance(int(ma), int):
                await ctx.send(f'Incorrect usage. Please use `{prefix}random [minimum] [maximum]` with integer values.')
                return
            output = rand.randint(int(mi), int(ma))
            await ctx.send(f'Your random number is: {output}')
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    @bot.command()
    @has_required_perm()
    async def addrole(ctx, member: discord.Member, role: discord.Role):
        try:
            await member.add_roles(role)
            await ctx.send(f"{member.display_name} has been given the {role.name} role.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @bot.command()
    @has_required_perm()
    async def removerole(ctx, member: discord.Member, role: discord.Role):
        try:
            await member.remove_roles(role)
            await ctx.send(f"{member.display_name} has had the {role.name} role removed.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")




    














    # Define help command
    @bot.command()
    async def h(ctx, typ=None):
        if not typ:
            prefix=config['prefix']
            owner_id=config['owner_id']
            owner = await bot.fetch_user(owner_id)
            help_msg =(f'''**Commands:**
            `{prefix}h` - Show this help message.
            `{prefix}ticket` - Make a ticket of player support.
            `{prefix}about_me` - Tells you a few things about your user ID.
            `{prefix}random <min> <max>` - Gives you a random number.
            For Moderation commands type {prefix}h mod
            For Owner commands type {prefix}h owner
            For More Info Contact <@{owner.id}>''')

            await ctx.send(help_msg)
            return
        elif typ == 'owner':
            prefix=config['prefix']
            owner_id=config['owner_id']
            owner = await bot.fetch_user(owner_id)
            help_msg= (f'''**Commands:**
            `{prefix}set_status` - Custom Status.
            `{prefix}clear_status` - Clears Custom Status.
            `{prefix}shutdown` - Shutsdown the bot
            For More Info Contact <@{owner.id}>''')
            await ctx.send(help_msg)
            return
        elif typ == 'mod':
            prefix=config['prefix']
            owner_id=config['owner_id']
            owner = await bot.fetch_user(owner_id)
            help_msg= (f'''**Commands:**
            `{prefix}ban <member> <reason>` - Bans a member from the server.
            `{prefix}unban <member>` - Unbans a member from the server.
            `{prefix}kick <member>` - Kicks a member from the server.
            `{prefix}mute <member>` - Mutes a member of the server.
            `{prefix}unmute <member>` - Unmutes a member of the server
            `{prefix}set_nickname <member>` - Changes nickname of a member.
            `{prefix}nickname <value>` - Changes nickname of the bot.
            `{prefix}close` - Closes a ticket.
            `{prefix}addrole <member> <role>` - Adds a role to a member.
            `{prefix}removerole <member> <role>` - Remove role from a member.
            For More Info Contact <@{owner.id}>''')
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
        
        if latest_release.tag_name > current_version:
            print(f'New version {latest_release.tag_name} available!')
            print(f'Download URL: {latest_release.html_url}')
            messagebox.showinfo(title="Va's BOT", message=m, icon=messagebox.INFO)



    check_for_updates()    

    # Start the bot
    bot.run(config['bot_token'])
