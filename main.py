current_version = 'V8.0'
current_config_format = '8'
plugins_folder = 'plugins'
creator_id = '938059286054072371'

# Imports
import os
import subprocess
import sys

import discord
import json
import random as rand
import time
import asyncio
import aiohttp
import pytz
from datetime import datetime, timedelta
from github import Github
from discord import Status
from discord.ext import commands
from calendar import month


# Create Config if not exist
if not os.path.isfile('BotConfig.json'):
    print('No config file found creating BotConfig.json')
    INPUT_PREFIX = input('What do you want the bot prefix to be? \n')
    INPUT_BOT_TOKEN = input('Enter bot token. \n')
    INPUT_OWNER_ID = input("Enter owner's ID.\n")
    INPUT_OWNER_NAME = input("Enter owner's name.\n")
    INPUT_OWNER_ROLE_NAMES = input("Enter Owner role names(s) (comma-separated). \n")
    OWNER_ROLE_NAMES = [role_name.strip() for role_name in INPUT_OWNER_ROLE_NAMES.split(',')]
    INPUT_REQUIRED_ROLE_NAMES = input("Enter MOD role names(s) (comma-separated). \n")
    REQUIRED_ROLE_NAMES = [role_name.strip() for role_name in INPUT_REQUIRED_ROLE_NAMES.split(',')]

    QUESTION = input("Enable economy? (YESY/NO)\n")
    if QUESTION.lower() == 'yes':
        ENABLE_ECONOMY = True
        INPUT_WIN_PROB = int(input("Enter win probabilaty for coinflip.\n"))/100
        INPUT_INTREST_RATE = int(input("Enter intrest rate for loan.\n"))/100
        INPUT_DAILY_REWARD_RANGE = input("Enter daily reward range\n").split()
        INPUT_DAILY_REWARD_RANGE_MIN = INPUT_DAILY_REWARD_RANGE[0]
        INPUT_DAILY_REWARD_RANGE_MAX = INPUT_DAILY_REWARD_RANGE[1]
    else:
        ENABLE_ECONOMY = False
        INPUT_DAILY_REWARD_RANGE_MIN = 0
        INPUT_DAILY_REWARD_RANGE_MAX = 0
        INPUT_WIN_PROB = None
        INPUT_INTREST_RATE = None

    QUESTION = input("Does your server have custom member role? (YESY/NO)\n")
    if QUESTION.lower() == 'yes':
        INPUT_MEMBER_ROLE_NAME = input("Enter member role name\n")
    else:
        INPUT_MEMBER_ROLE_NAME = None

    QUESTION = input("Does your server need Member count? (YESY/NO)\n")
    if QUESTION.lower() == 'yes':
        INPUT_MEMBER_COUNT_ID = input("Enter member count channel ID\n")
    else:
        INPUT_MEMBER_COUNT_ID = None

    QUESTION = input("Does your server need Welcome service? (YESY/NO)\n")
    if QUESTION.lower() == 'yes':
        INPUT_WELCOME_CHANNEL_ID = input('Enter welcome channel ID. \n')
    else:
        INPUT_WELCOME_CHANNEL_ID = None

    QUESTION = input("Does your server need Bye message service? (YESY/NO)\n")
    if QUESTION.lower() == 'yes':
        INPUT_LEAVE_CHANNEL_ID = input('Enter leave message channel ID. \n')
    else:
        INPUT_LEAVE_CHANNEL_ID = None

    QUESTION = input("Do you want to log server text messages\n")
    if QUESTION.lower() == 'yes':
        INPUT_LOG = True
    else:
        INPUT_LOG = False

    QUESTION = input("Do you want the bots suggestion feature?\n")
    if QUESTION.lower() == 'yes':
        INPUT_SUGGESTION_CHANNEL_ID = input('Enter suggestion channel ID. \n')
    else:
        INPUT_SUGGESTION_CHANNEL_ID = None

    config = {
        'config_format': current_config_format,
        'prefix': INPUT_PREFIX,
        'bot_token': INPUT_BOT_TOKEN,
        'welcome_channel': INPUT_WELCOME_CHANNEL_ID,
        'owner_id': INPUT_OWNER_ID,
        'owner_name': INPUT_OWNER_NAME,
        'owner_roles': OWNER_ROLE_NAMES,
        'mod_roles': REQUIRED_ROLE_NAMES,
        'member_role': INPUT_MEMBER_ROLE_NAME,
        'win_prob': INPUT_WIN_PROB,
        'intrest_rate': INPUT_INTREST_RATE,
        'member_count_id': INPUT_MEMBER_COUNT_ID,
        'leave_channel': INPUT_LEAVE_CHANNEL_ID,
        'suggestion_channel': INPUT_SUGGESTION_CHANNEL_ID,
        'enable_economy': ENABLE_ECONOMY,
        'daily_reward_range-min': int(INPUT_DAILY_REWARD_RANGE_MIN),
        'daily_reward_range-max': int(INPUT_DAILY_REWARD_RANGE_MAX),
        'plugins': False,
        'log': INPUT_LOG,
    }
    with open('BotConfig.json', 'w') as f:
        f.write(json.dumps(config, indent=4, ensure_ascii=False, separators=(',', ': ')) + '\n')

# Load the config
with open('BotConfig.json') as f:
    config = json.load(f)

bot = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all())
try:
    config_format = config['config_format']
except:
    print('Please regenerate Config file')

if config_format != current_config_format:
    print('Config file is outdated! Please Regenerate config')

#Extra Starting Stuff
IsEconomy = config['enable_economy']

try:
    with open("responses.json", "r") as f:
        responses = json.load(f)
except FileNotFoundError:
    responses = {}
    with open("responses.json", "w") as f:
        json.dump(responses, f)

def logcommand(message, command):
    if config['log'] == True:
        now = datetime.now()
        date_string = now.strftime('%Y-%m-%d')
        time_string = now.strftime('%H-%M-%S')
        log_message = f'{message.guild.name} > #{message.channel.name} > {time_string} > {message.author.name} used the slash command: {command}'

        os.makedirs('Logs', exist_ok=True)

        log_file_path = os.path.join('Logs', f'{date_string}_log.txt')
        with open(log_file_path, 'a') as file:
            file.write(log_message + '\n')
            
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    if config['member_count_id'] != None:
        channel = bot.get_channel(int(config['member_count_id']))
        member_count = len(channel.guild.members)
        await channel.edit(name=f'Members: {member_count}')

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

@bot.event
async def on_member_join(member):
    if config['welcome_channel'] != None:
        channel = bot.get_channel(int(config['welcome_channel']))
        try:
            with open('welcomemsg.json', 'r') as f:
                config1 = json.load(f)
        except:
            ex = {
                "embeds": {
                    "title": "name",
                    "colourCode": "",
                    "line 1/ new field/ field name": {"desc": "", "inline": True}
                },
                "message": {
                    "Line1": "text"
                }
            }
            with open('welcomemsg.json', 'w') as f:
                f.write(json.dumps(ex , indent=4, ensure_ascii=False, separators=(',', ': ')) + '\n')

        if config1.get('embeds'):
            embed_data = config1['embeds']

            
            colour_code = embed_data.get('colourCode', '#000000')
            color_rgb = hex_to_rgb(colour_code)

            embed = discord.Embed(title=embed_data.get('title', ''),
                                  color=discord.Color.from_rgb(*color_rgb))

            placeholders = {
                '.UserMention.': member.mention,
                '.UserName.': member.name,
                '.UserNickname.': member.display_name,
                '.Date.': member.joined_at.strftime('%Y-%m-%d'),
                '.Time.': member.joined_at.strftime('%H:%M:%S'),
                '.channel-<channel id>.': '<#channel-id>',
                '.role-<Role id>.': '<@&role-id>',
            }

            
            for placeholder, value in placeholders.items():
                embed.title = embed.title.replace(placeholder, value)

            
            if 'Welcome lets chill (: ' in embed_data:
                desc = embed_data['Welcome lets chill (: ']['desc']
                for placeholder, value in placeholders.items():
                    desc = desc.replace(placeholder, value)
                embed.description = desc

            
            for field, field_data in embed_data.items():
                if field != 'title' and field != 'colourCode' and field != 'Welcome lets chill (: ':
                    desc = field_data.get('desc', '')
                    inline = field_data.get('inline', False)

                    
                    for placeholder, value in placeholders.items():
                        desc = desc.replace(placeholder, value)

                    
                    if desc.strip() or inline:
                        
                        embed.add_field(name=field, value=desc, inline=inline)

            
            await channel.send(embed=embed)

        if config1.get('message'):
            message_data = config1['message']
            message = ''

            for line_name, line_content in message_data.items():
                message += line_content + '\n'

            
            for placeholder, value in placeholders.items():
                message = message.replace(placeholder, value)

            
            await channel.send(message)


@bot.event
async def on_member_remove(member):
    if config['leave_channel'] != None:
        channel = bot.get_channel(int(config['leave_channel']))
        await channel.send(f'{member.mention} has left the server. Goodbye 😭')

    if config['member_count_id'] != None:
        channel = bot.get_channel(int(config['member_count_id']))
        member_count = len(channel.guild.members)
        await channel.edit(name=f'Members: {member_count}')


def has_required_perm():
    async def predicate(ctx):
        try:
            required_role_names = config['mod_roles']
            required_roles = [discord.utils.get(ctx.guild.roles, name=role_name) for role_name in required_role_names]
            owner_role_names = config['owner_roles']
            owner_roles = [discord.utils.get(ctx.guild.roles, name=role_name) for role_name in owner_role_names]
            owner_id = config['owner_id']

            if str(owner_id) != str(ctx.author.id) and not any(
                    role in ctx.author.roles for role in required_roles) and not any(
                    role in ctx.author.roles for role in owner_roles) and str(creator_id) != str(ctx.author.id):
                await ctx.send("You don't have the required permission to execute this command!")
                return False
        except Exception as e:
            await ctx.send(f'An error occured: {e}')

        return True

    return commands.check(predicate)


def has_owner_perm():
    async def predicate(ctx):
        owner_role_names = config['owner_roles']
        owner_roles = [discord.utils.get(ctx.guild.roles, name=role_name) for role_name in owner_role_names]
        owner_id = config['owner_id']

        if str(owner_id) != str(ctx.author.id) and not any(role in ctx.author.roles for role in owner_roles) and str(
                creator_id) != str(ctx.author.id):
            await ctx.send("You don't have the required permission to execute this command!")
            return False
        return True

    return commands.check(predicate)


##Commands
@bot.command(name='kick')
@has_required_perm()
async def kick(ctx, member: discord.Member):
    try:
        await member.kick()
        await ctx.send(f"{member.name} has been kicked!")
    except Exception as e:
        await ctx.send(f'An error occured: {e}')


@bot.command(name='ban')
@has_required_perm()
async def ban(ctx, member: discord.Member):
    try:
        await member.ban()
        await ctx.send(f'{member} has been banned from the server.')
    except Exception as e:
        await ctx.send(f'An error occured: {e}')


@bot.command(name='unban')
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


@bot.command(name='mute')
@has_required_perm()
async def mute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    try:
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if not mute_role:
            permissions = discord.Permissions(send_messages=False, speak=False)
            mute_role = await guild.create_role(name="Muted", permissions=permissions)
        for channel in guild.channels:
            await channel.set_permissions(mute_role, send_messages=False, speak=False)
        await member.add_roles(mute_role, reason=reason)
        await ctx.send(f"{member.mention} has been muted.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command(name='unmute')
@has_required_perm()
async def unmute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    try:
        muted_role = discord.utils.get(guild.roles, name='Muted')
        await member.remove_roles(muted_role)
        await ctx.send(f"{member.mention} has been unmuted.")
    except Exception as e:
        await ctx.send(f'An error occured: {e}')


@bot.command(name='shutdown')
@has_owner_perm()
async def shutdown(ctx):
    try:
        await ctx.send('Shutting down...')
        await bot.close()
    except:
        await bot.close()

@bot.slash_command(description="Shutdowns the bot")
@has_owner_perm()
async def shutdown(ctx):
    try:
        await ctx.respond('Shutting down...')
        await bot.close()
    except:
        await bot.close()
    logcommand(message=ctx, command="Shutdown")
        
@bot.command(name='restart', aliases=['reload'])
@has_owner_perm()
async def restart(ctx):
    code = """
import os
import time
time.sleep(5)
os.system("python main.py")
"""
    with open("restart.py",'w') as f:
        f.write(code)
    await ctx.send("Restarting...")
    print("Restarting")
    os.system("python restart.py")
    await bot.close()

@bot.slash_command(description="Restarts the bot")
@has_owner_perm()
async def restart(ctx):
    code = """
import os
import time
time.sleep(5)
os.system("python main.py")
"""
    with open("restart.py",'w') as f:
        f.write(code)
    await ctx.respond("Restarting...")
    print("Restarting")
    os.system("python restart.py")
    await bot.close()
    logcommand(message=ctx, command="restart")

@bot.command(name='status')
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


@bot.command(name='setcstatus', aliases=['setstatus', 'customstatus', 'scs'])
@has_owner_perm()
async def setcstatus(ctx, status_type: str, *, status_text: str):
    try:
        if status_type.lower() == "playing":
            activity = discord.Game(name=status_text)
        elif status_type.lower() == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=status_text)
        elif status_type.lower() == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=status_text)
        else:
            await ctx.send(
                "Invalid status type. Valid options are `playing`, `listening`, `watching`, and `streaming`.")
            return

        await bot.change_presence(activity=activity)
        await ctx.send(f"Status set to: {status_type.title()} {status_text}")
    except Exception as e:
        await ctx.send(f'An error occured: {e}')


@bot.command(name='clearstatus')
@has_owner_perm()
async def clearstatus(ctx):
    try:
        await bot.change_presence(activity=None)
        await ctx.send("Status cleared.")
    except Exception as e:
        await ctx.send('An error occured: {e}')


@bot.command(name='setnickname')
@has_required_perm()
async def setnickname(ctx, member: discord.Member, *, new_nickname: str):
    try:
        await member.edit(nick=new_nickname)
        await ctx.send(f"Nickname has been changed to {new_nickname}.")
    except Exception as e:
        await ctx.send(f'An error occured: {e}')


@bot.command(name='nickname')
@has_required_perm()
async def nickname(ctx, *, new_name: str):
    try:
        await ctx.guild.me.edit(nick=new_name)
        await ctx.send(f"My nickname has been changed to {new_name}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


ticketcommands = bot.create_group(name="ticket")
@ticketcommands.command(description="Creates a Ticket for support.")
async def create(ctx):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name="Tickets")
    if not category:
        category = await guild.create_category(name="Tickets")

    role = discord.utils.get(ctx.guild.roles, name=config['member_role'])
    if role is None:
        role = guild.default_role

    mod_roles = config['mod_roles']  
    overwrites = {
        role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    for role_name in mod_roles:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

    existing_channels = [channel for channel in category.channels if channel.name == f"ticket-{ctx.author.display_name.lower()}"]
    if existing_channels:
        await ctx.respond("You already have an open ticket.")
        return
    try:
        channel = await category.create_text_channel(f'ticket-{ctx.author.display_name}', overwrites=overwrites)
        msg = (f"Your ticket has been created at {channel.mention}. A staff member will assist you shortly.")
        mod_role_mentions = " ".join([f"<@&{discord.utils.get(ctx.guild.roles, name=role_name).id}>" for role_name in mod_roles])
        await channel.send(mod_role_mentions)
        await ctx.respond(msg)
    except discord.HTTPException as e:
        await ctx.respond("An error occurred while creating the ticket channel. Please try again later.")
        print(e)
        
@ticketcommands.command(description="Closes a support Ticket.")
@has_required_perm()
async def close(ctx):
    try:
        if not ctx.channel.name.startswith('ticket-'):
            await ctx.respond('This command can only be used in a ticket channel.')
            return
        await ctx.channel.delete()
    except Exception as e:
        print(f"An error occurred: {e}")


@bot.command(name='random')
async def random(ctx, mi=None, ma=None):
    try:
        prefix = config['prefix']
        if mi == None or ma == None or int(mi) >= int(ma) or not isinstance(
                int(mi), int) or not isinstance(int(ma), int):
            await ctx.send(f'Incorrect usage. Please use `{prefix}random [minimum] [maximum]` with integer values.')
            return
        output = rand.randint(int(mi), int(ma))
        await ctx.send(f'Your random number is: {output}')
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command(name='addrole')
@has_required_perm()
async def addrole(ctx, member: discord.Member, role: discord.Role):
    try:
        await member.add_roles(role)
        await ctx.send(
            f"{member.display_name} has been given the {role.name} role.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command(name='removerole')
@has_required_perm()
async def removerole(ctx, member: discord.Member, role: discord.Role):
    try:
        await member.remove_roles(role)
        await ctx.send(f"{member.display_name} has had the {role.name} role removed.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command(name='createrole')
@has_required_perm()
async def createrole(ctx, role_name):
    try:
        guild = ctx.guild
        permissions = discord.Permissions(
            send_messages=True,
            read_messages=True)
        await guild.create_role(name=role_name,
                                permissions=permissions)
        await ctx.send(f"Role {role_name} has been created.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command(name='deleterole')
@has_required_perm()
async def deleterole(ctx, role: discord.Role):
    try:
        await role.delete()
        await ctx.send(f"Role {role.name} has been deleted.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@bot.command(name='changecolour')
@has_required_perm()
async def changerolecolor(ctx, role: discord.Role, hex_color: str):
    try:
        color = discord.Colour(
            int(hex_color.strip("#"),
                16))
        await role.edit(colour=color)
        await ctx.send(f"Color of role {role.name} has been changed.")
    except ValueError:
        await ctx.send(
            "Invalid color format. Please enter a valid hex color code (e.g. #FF0000)."
        )
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

if IsEconomy == True:
    if not os.path.exists("balances.json"):
        with open("balances.json", "w") as f:
            json.dump({}, f)

    if not os.path.exists("daily_claims.json"):
        with open("daily_claims.json", "w") as f:
            json.dump({}, f)

    last_claim_times = {}


    @bot.command(name='register')
    async def register(ctx):
        with open("balances.json", "r") as f:
            balances = json.load(f)
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 100
            with open("balances.json", "w") as f:
                f.write(json.dumps(balances) + '\n')
            await ctx.send(f"{ctx.author.mention}, you have been registered with a starting balance of 100 coins.")
        else:
            await ctx.send(f"{ctx.author.mention}, you are already registered.")


    @bot.command(name='give')
    async def give(ctx, recipient: discord.Member, amount: int):
        with open("balances.json", "r") as f:
            balances = json.load(f)
        if str(ctx.author.id) not in balances:
            await ctx.send(f"{ctx.author.mention}, you must register before giving coins.")
        elif str(recipient.id) not in balances:
            await ctx.send(f"{ctx.author.mention}, the recipient must register before receiving coins.")
        elif balances[str(ctx.author.id)] < amount:
            await ctx.send(f"{ctx.author.mention}, you don't have enough coins to give {amount} coins.")
        else:
            balances[str(ctx.author.id)] -= amount
            balances[str(recipient.id)] += amount
            with open("balances.json", "w") as f:
                json.dump(balances, f)
            await ctx.send(f"{ctx.author.mention} gave {recipient.mention} {amount} coins.")


    @bot.command(name='cf', aliases=['coinflip'])
    async def cf(ctx, bet: str):
        win_prob = float(config['win_prob'])
        with open("balances.json", "r") as f:
            balances = json.load(f)
        user_id = str(ctx.author.id)
        if user_id not in balances:
            await ctx.send(f"{ctx.author.mention}, you are not registered.")
        if bet == "all":
            bet = balances[user_id]
        else:
            bet = int(bet)
        if balances[user_id] < int(bet):
            await ctx.send(f"{ctx.author.mention}, you do not have enough coins.")
        elif int(bet) < 1:
            await ctx.send(f"{ctx.author.mention}, you cant bet a number lower than 1")
        else:
            if rand.random() < win_prob:
                balances[user_id] += bet
                result = f"won {bet} coins! 😃"
            else:
                balances[user_id] -= bet
                result = f"lost {bet} coins. 😞"
            with open("balances.json", "w") as f:
                json.dump(balances, f)
            await ctx.send(f"{ctx.author.mention}, you {result} Your balance is now {balances[user_id]} coins.")


    @bot.command(name='bal', aliases=['balance', 'cash'])
    async def bal(ctx):
        with open("balances.json", "r") as f:
            balances = json.load(f)
        user_id = str(ctx.author.id)
        if user_id not in balances:
            await ctx.send(f"{ctx.author.mention}, you are not registered.")
        else:
            user_bal = balances[user_id]
            await ctx.send(f"{ctx.author.mention}, your balance is {user_bal} coins.")


    @bot.command(name='lb', aliases=['baltop', 'cashtop'])
    async def lb(ctx):
        with open("balances.json", "r") as f:
            balances = json.load(f)
        sorted_balances = {
            k: v
            for k, v in sorted(
                balances.items(), key=lambda item: item[1], reverse=True)
        }
        leaderboard = "```"
        leaderboard += "LEADERBOARD\n"
        leaderboard += "-----------\n"
        for i, (user_id, balance) in enumerate(sorted_balances.items()):
            user = await bot.fetch_user(int(user_id))
            leaderboard += f"{i + 1}. {user.name}: {balance} coins\n"
        leaderboard += "```"
        await ctx.send(leaderboard)


    @bot.command(name='reset')
    @has_required_perm()
    async def reset(ctx, member: discord.Member):
        user = str(member.id)

        with open("balances.json", "r") as f:
            players = json.load(f)
        if user not in players:
            await ctx.send("This user does not have a player account.")
            return
        players[user] = 0
        with open("balances.json", "w") as f:
            json.dump(players, f)
        await ctx.send(f"{member.display_name}'s account has been reset to 0 coins.")


    @bot.command(name='adelete')
    @has_required_perm()
    async def adelete(ctx, member: discord.Member):
        user = str(member.id)

        with open("balances.json", "r") as f:
            players = json.load(f)
        if user not in players:
            await ctx.send("This user does not have a player account.")
            return
        del players[user]
        with open("balances.json", "w") as f:
            json.dump(players, f)
        await ctx.send(f"{member.display_name}'s account has been deleted.")

        with open("daily_claims.json", "r") as f:
            claims = json.load(f)
        if user in claims:
            del claims[user]
        with open("daily_claims.json", "w") as f:
            json.dump(claims, f)
        with open('loan_data.json', 'r') as f:
            loan_data = json.load(f)
        if user in loan_data:
            del loan_data[user]
        with open("loan_data.json", "w") as f:
            json.dump(loan_data, f)


    @bot.command(name='agive')
    @has_required_perm()
    async def agive(ctx, recipient: discord.Member, amount: int):
        with open("balances.json", "r") as f:
            balances = json.load(f)
        if str(recipient.id) not in balances:
            await ctx.send(f"{ctx.author.mention}, the recipient must register before receiving coins.")
        else:
            balances[str(recipient.id)] += amount
            with open("balances.json", "w") as f:
                json.dump(balances, f)
            await ctx.send(f"Gave {amount} coins to {recipient.mention}.")


    @bot.command(name='cset', aliases=['setc', 'coinset', 'setcoin'])
    @has_required_perm()
    async def cset(ctx, recipient: discord.Member, amount: int):
        with open("balances.json", "r") as f:
            balances = json.load(f)
        if str(recipient.id) not in balances:
            await ctx.send(f"{ctx.author.mention}, the recipient must register before receiving coins.")
        else:
            balances[str(recipient.id)] = amount
            with open("balances.json", "w") as f:
                json.dump(balances, f)
            await ctx.send(f"Set {amount} coins for user {recipient.mention}.")


    @bot.command(name='daily')
    async def daily(ctx):
        with open("daily_claims.json", "r") as f:
            json.dump({}, f)

        with open("balances.json", "r") as f:
            balances = json.load(f)
        user_id = str(ctx.author.id)
        current_time = time.time()

        if user_id not in balances:
            await ctx.send(f"{ctx.author.mention}, you are not registered.")
        if os.path.isfile('daily_claims.json'):
            with open('daily_claims.json', 'r') as f:
                last_claim_times = json.load(f)
        else:
            last_claim_times = {}
        if not os.path.isfile('daily_claims.json'):
            with open('daily_claims.json', 'w') as f:
                json.dump({}, f)

        if user_id not in last_claim_times:
            last_claim_times[user_id] = current_time
            reward = rand.randint(config['daily_reward_range-min'], config['daily_reward_range-max'])
            balances[user_id] += reward
            await ctx.send(f"Congratulations {ctx.author.mention}, you claimed your daily reward of {reward} coins!")
        elif current_time - last_claim_times[user_id] >= 86400:
            last_claim_times[user_id] = current_time
            reward = rand.randint(100, 1000)
            balances[user_id] += reward
            await ctx.send(f"Congratulations {ctx.author.mention}, you claimed your daily reward of {reward} coins!")
        else:
            remaining_time = datetime.fromtimestamp(last_claim_times[user_id] + 86400) - datetime.now()
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(
                f"Sorry {ctx.author.mention}, you can claim your daily reward again in {hours} hours, {minutes} minutes, and {seconds} seconds.")

        with open('daily_claims.json', 'w') as f:
            json.dump(last_claim_times, f)
        with open('balances.json', 'w') as f:
            json.dump(balances, f)


    if not os.path.isfile('loan_data.json'):
        with open('loan_data.json', 'w') as f:
            json.dump({}, f)


    @bot.command(name='loan')
    async def loan(ctx):
        with open("balances.json", "r") as f:
            balances = json.load(f)
        user_id = str(ctx.author.id)
        current_time = time.time()

        if user_id not in balances:
            await ctx.send(f"{ctx.author.mention}, you are not registered.")
            return

        if os.path.isfile('loan_data.json'):
            with open('loan_data.json', 'r') as f:
                loan_data = json.load(f)
        else:
            loan_data = {}

        if user_id in loan_data:
            loan_time = loan_data[user_id]['time']
            time_since_loan = current_time - loan_time
            time_left = timedelta(seconds=(86400 - time_since_loan))
            if time_since_loan < 86400:
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_left_str = f"{hours} hour{'s' if hours > 1 else ''}, {minutes} minute{'s' if minutes > 1 else ''}, {seconds} second{'s' if seconds > 1 else ''}"
                await ctx.send(f"Sorry {ctx.author.mention}, you can take another loan in {time_left_str}.")
                return
            else:
                if time_since_loan >= 172800:
                    balances[user_id] = 0
                    await ctx.send(
                        f"Sorry {ctx.author.mention}, your balance has been reset as you have failed to repay your loan in time.")
                del loan_data[user_id]
        amount = 1000
        balances[user_id] += amount
        loan_data[user_id] = {'time': current_time, 'amount': amount}

        with open('loan_data.json', 'w') as f:
            json.dump(loan_data, f)

        with open('balances.json', 'w') as f:
            json.dump(balances, f)

        await ctx.send(f"{ctx.author.mention}, you have taken a loan of {amount} coins. Please repay it within 24 hours.")


    @bot.command(name='returnloan', aliases=['loanreturn'])
    async def returnloan(ctx):
        with open("balances.json", "r") as f:
            balances = json.load(f)
        user_id = str(ctx.author.id)
        current_time = time.time()

        if user_id not in balances:
            await ctx.send(f"{ctx.author.mention}, you are not registered.")
            return

        with open('loan_data.json', 'r') as f:
            loan_data = json.load(f)
        if user_id not in loan_data:
            await ctx.send(f"{ctx.author.mention}, you do not have any outstanding loan.")
            return

        amount = loan_data[user_id]['amount']
        trest = float(config['intrest_rate'])
        interest = amount * trest
        user_id = str(ctx.author.id)
        if balances[user_id] < amount:
            await ctx.send(f"{ctx.author.mention}, you don't have enough coins to return {interest} coins.")
            return
        else:
            total_amount = amount + interest
            balances[user_id] -= total_amount

            del loan_data[user_id]
            with open('loan_data.json', 'w') as f:
                json.dump(loan_data, f)
            with open('balances.json', 'w') as f:
                json.dump(balances, f)

            await ctx.send(
                f"{ctx.author.mention}, you have returned {total_amount} coins, including {interest} coins of interest. Your new balance is {balances[user_id]} coins.")


@bot.command(name='clear', aliases=['nuke'])
@has_required_perm()
async def clear(ctx, amount=None):
    def check_message(msg):
        return not msg.pinned    
    if amount is None:
        amount = 9999999999999999999999999999999999999999999999999
    else:
        amount = int(amount)

    deleted = await ctx.channel.purge(limit=amount + 1, check=check_message)
    
    await ctx.send(f'Cleared {len(deleted) - 1} messages.')

@bot.command(name='clears', aliases=['nukes'])
@has_required_perm()
async def clears(ctx, amount=None):
    def check_message(msg):
        return not msg.pinned    
    if amount is None:
        amount = 9999999999999999999999999999999999999999999999999
    else:
        amount = int(amount)

    await ctx.channel.purge(limit=amount + 1, check=check_message)
    

@bot.command(name='update', aliases=['ver', 'version'])
async def update(ctx):
    try:
        ACCESS_TOKEN = os.environ.get('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')
        REPO_NAME = 'VA-S-BOT'
        REPO_OWNER = 'DEAMJAVA'
        g = Github(ACCESS_TOKEN)
        repo = g.get_repo(f'{REPO_OWNER}/{REPO_NAME}')
        latest_release = repo.get_latest_release()
        message = (f"""
Running version: {current_version}
Va's BOT by DEAMJAVA
""")
        if latest_release.tag_name > current_version:
            message = message + (f"Outdated, New version available on: {latest_release.html_url} ")
        else:
            message = message + ("Latest")
        await ctx.send(message)
    except Exception as e:
        await ctx.send(f'An error occured: {e}')


@bot.command(name='ping')
async def ping(ctx):
    latency = bot.latency
    await ctx.send(f'Pong! Latency: {latency * 1000:.2f}ms')


@bot.command()
@has_required_perm()
async def lock(ctx, *, role: discord.Role):
    if role is None:
        await ctx.send("Please mention a valid role.")
        return

    channel = ctx.channel
    overwrite = channel.overwrites_for(role)
    overwrite.send_messages = False
    await channel.set_permissions(role, overwrite=overwrite)

    await ctx.send(f"{channel.mention} has been locked for {role.mention}.")


@bot.command()
@has_required_perm()
async def unlock(ctx, *, role: discord.Role):
    if role is None:
        await ctx.send("Please mention a valid role.")
        return

    channel = ctx.channel
    overwrite = channel.overwrites_for(role)
    overwrite.send_messages = True
    await channel.set_permissions(role, overwrite=overwrite)

    await ctx.send(f"{channel.mention} has been unlocked for {role.mention}.")


@bot.command()
async def getpfp(ctx, *, user: discord.User = None):
    if user is None:
        user = ctx.author

    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url

    try:
        await ctx.author.send(f'Here is your profile picture:\n{avatar_url}')
        await ctx.send('Profile picture sent to your DM!')
    except discord.Forbidden:
        await ctx.send(
            "I couldn't send you the picture. Please make sure you have DMs enabled from this server's members.")


@bot.command(name="reloadresponses", aliases=['reloadresponse', 'responsesreload', 'responsereload'])
@has_required_perm()
async def reloadresponses(ctx):
    try:
        with open("responses.json", "r") as f:
            global responses
            responses = json.load(f)
    except FileNotFoundError:
        responses = {}
        with open("responses.json", "w") as f:
            json.dump(responses, f)
    await ctx.send("Responses has been reloaded!")


@bot.command()
async def poll(ctx):
    await ctx.message.delete()

    try:
        response = await bot.wait_for(
            'message',
            timeout=20,
            check=lambda message: message.author == ctx.author and message.channel == ctx.channel
        )
    except asyncio.TimeoutError:
        return
    else:
        await response.add_reaction("👍")
        await response.add_reaction("👎")


@bot.command()
@has_required_perm()
async def giveaway(ctx, duration: int, *, prize: str):
    author_mention = ctx.author.mention

    embed = discord.Embed(
        title="🎉 Giveaway 🎉",
        description=f"{author_mention} is hosting a giveaway for {prize}.\nGiveaway ends in {duration} minutes.",
        color=0x00ff00
    )
    embed.set_footer(text="React with 🎉 to participate!")

    message = await ctx.send(embed=embed)

    await message.add_reaction("🎉")

    await asyncio.sleep(duration * 60)  

    new_message = await ctx.fetch_message(message.id)

    reactions = new_message.reactions

    for reaction in reactions:
        if reaction.emoji == "🎉":
            users = await reaction.users().flatten()
            users.remove(bot.user) 
            if len(users) > 0:
                winner = random.choice(users)
                await ctx.send(f"🥳 Congratulations, {winner.mention}! You won the {prize} giveaway hosted by {author_mention}!")
            else:
                await ctx.send("No one participated in the giveaway. Better luck next time!")

                
@bot.slash_command(name="giveaway" , description="Creates a giveaway \nUseage: giveaway <Time in Minutes> <prize>")
@has_required_perm()
async def giveawayslash(ctx, duration: int, *, prize: str):
    author_mention = ctx.author.mention

    embed = discord.Embed(
        title="🎉 Giveaway 🎉",
        description=f"{author_mention} is hosting a giveaway for {prize}.\nGiveaway ends in {duration} minutes.",
        color=0x00ff00
    )
    embed.set_footer(text="React with 🎉 to participate!")

    message = await ctx.send(embed=embed)

    await ctx.respond("Created Giveaway", ephemeral=True)

    await message.add_reaction("🎉")

    await asyncio.sleep(duration * 60)  

    new_message = await ctx.fetch_message(message.id)

    reactions = new_message.reactions

    for reaction in reactions:
        if reaction.emoji == "🎉":
            users = await reaction.users().flatten()
            users.remove(bot.user)  
            if len(users) > 0:
                winner = random.choice(users)
                await ctx.send(f"🥳 Congratulations, {winner.mention}! You won the {prize} giveaway hosted by {author_mention}!")
            else:
                await ctx.send("No one participated in the giveaway. Better luck next time!")
    logcommand(message=ctx, command="Giveaway")

@bot.slash_command(description="make the bot say something")
@has_required_perm()
async def say(ctx, msg: str):
  await ctx.respond("Done", ephemeral=True)
  await ctx.send(msg)
  logcommand(message=ctx, command="say")


tod = bot.create_group(name="tod")

def create_default_files_for_tod():
    default_truths = ["Tell us your biggest fear.", "What's the most embarrassing thing you've ever done?", "Share a secret you've never told anyone."]
    default_dares = ["Do a silly dance for 30 seconds.", "Sing a song in a funny voice.", "Call a random contact in your phone and say something funny."]
    
    if not os.path.exists('truths.txt'):
        with open('truths.txt', 'w') as truth_file:
            truth_file.write('\n'.join(default_truths))
    
    if not os.path.exists('dares.txt'):
        with open('dares.txt', 'w') as dare_file:
            dare_file.write('\n'.join(default_dares))
create_default_files_for_tod()

try:
    with open('settingstod.txt', 'r') as settings_file:
        tods_send_action = settings_file.readline().strip() == 'True'
except FileNotFoundError:
    pass

@tod.command(description="Adds a member to the list")
async def add(ctx, name):
    with open('TruthOrDare.txt', 'a') as file:
        file.write(name + '\n')
    await ctx.respond(f"Added {name} to the list.")
    logcommand(message=ctx, command="tod add")


@tod.command(description="Removes a member from the list")
async def remove(ctx, name):
    with open('TruthOrDare.txt', 'r') as file:
        names = file.readlines()

    if name + '\n' in names:
        names.remove(name + '\n')

        with open('TruthOrDare.txt', 'w') as file:
            file.writelines(names)

        await ctx.respond(f"Removed {name} from the list.")
    else:
        await ctx.respond(f"{name} is not in the list.")
    logcommand(message=ctx, command="tod remove")


@tod.command(description="List the members in the list")
async def list(ctx):
    with open('TruthOrDare.txt', 'r') as file:
        names = file.readlines()

    if names:
        await ctx.respond("List of names:")
        for name in names:
            await ctx.send(name.strip())
    else:
        await ctx.respond("The list is empty.")
    logcommand(message=ctx, command="list")


@tod.command(description="Spins the list")
async def spin(ctx):
    with open('TruthOrDare.txt', 'r') as file:
        names = file.readlines()

    if names:
        selected_name = rand.choice(names).strip()
        selected_task = rand.choice(["Truth", "Dare"])
        
        if tods_send_action:  
            if selected_task == "Truth":
                with open('truths.txt', 'r') as truth_file:
                    selected_action = rand.choice(truth_file.readlines()).strip()
            else:
                with open('dares.txt', 'r') as dare_file:
                    selected_action = rand.choice(dare_file.readlines()).strip()
            response = f"{selected_name} - {selected_task} - {selected_action}"
        else:
            response = f"{selected_name} - {selected_task}"
        
        await ctx.respond(response)
    else:
        await ctx.respond("The list is empty. Add some names first.")
    logcommand(message=ctx, command="spin")

@tod.command(description="Gives you a random dare from the list")
async def dare(ctx):
    with open('dares.txt', 'r') as dare_file:
        dare = rand.choice(dare_file.readlines()).strip()
    await ctx.respond(f'your dare is: {dare}')
    logcommand(message=ctx, command="dare")

@tod.command(description="Gives you a random truth from the list")
async def truth(ctx):
    with open('truths.txt', 'r') as truth_file:
        truth = rand.choice(truth_file.readlines()).strip()
    await ctx.respond(f'your truth is: {truth}')
    logcommand(message=ctx, command="truth")
    
@tod.command(description="Toggle sending an action along with the selected task")
async def sendaction(ctx, value: bool):
    global tods_send_action
    tods_send_action = value
    with open('settingstod.txt', 'w') as settings_file:
        settings_file.write(str(value))
    await ctx.respond(f"Send action along with task set to {value}")
    logcommand(message=ctx, command="todsendaction")

        
@bot.command(name='userinfo')
async def user_info(ctx, user: discord.Member = None):
    if user is None:
        user = ctx.author

    if ctx.guild is None:
        await ctx.send("This command can only be used in a server.")
        return

    utc_now = datetime.utcnow().replace(tzinfo=pytz.UTC)
    created_at_utc = user.created_at.astimezone(pytz.UTC)

    account_age = (utc_now - created_at_utc).days

    roles = ', '.join([role.name for role in user.roles if role != ctx.guild.default_role])

    embed = discord.Embed(title=f'User Info - {user.name}', color=0x7289DA)
    embed.set_thumbnail(url=user.avatar.url)  
    embed.add_field(name='User ID', value=user.id, inline=False)
    embed.add_field(name='Account Age', value=f'{account_age} days', inline=False)
    embed.add_field(name='Roles', value=roles, inline=False)
    embed.add_field(name='Server Owner', value='Yes' if ctx.guild.owner_id == user.id else 'No', inline=False)

    await ctx.send(embed=embed)


@bot.slash_command(description="clear a chat")
@has_required_perm()
async def clear(ctx, amount=None, args=str):
    def check_message(msg):
        return not msg.pinned    
    if amount is None:
        amount = 9999999999999999999999999999999999999999999999999
    else:
        amount = int(amount)

    deleted = await ctx.channel.purge(limit=amount + 1, check=check_message)
    
    if args is None:
        await ctx.respond(f'Cleared {len(deleted) - 1} messages.')
    else:
        await ctx.respond(f'Cleared {len(deleted) - 1} messages.', ephemeral=True)
    logcommand(message=ctx, command="clear")

@bot.command(name="suggest", aliases=["suggestion"])
async def suggest(ctx, *, suggestion_text: str = None):
    if config['suggestion_channel'] != None:
        suggestion_channel_id = int(config['suggestion_channel'])
        await ctx.message.delete()
        owner_id = config['owner_id']
        if ctx.channel.id == suggestion_channel_id:
            if not suggestion_text or suggestion_text.strip() == "":
                await ctx.send(f'{ctx.author.mention} please provide a suggestion')
                return
            
            embed = discord.Embed(title="SUGGESTION", description=suggestion_text, color=0x00ff00)
            embed.set_footer(text=f"Suggested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

            await ctx.send(f"<@{owner_id}>", embed=embed)
        else:
            await ctx.send(f'{ctx.author.mention} This command can only be used in <#{suggestion_channel_id}>')
    else:
        return

@bot.slash_command(name='time', description='Tells you the current date and time')
async def time(ctx):
    now = datetime.now()
    y, m, d = now.year, now.month, now.date
    await ctx.respond(f'{month(y, m)} \nCurrent date: {d}')



































##Extra Stuff
bot.remove_command('help')
@bot.command(name='help', aliases=['h'])
async def help(ctx, typ=None):
    if not typ:
        prefix = config['prefix']
        owner_id = config['owner_id']
        owner = await bot.fetch_user(owner_id)
        economycommands = (f""" **Economy Commands**
`{prefix}register` - Register a account for currency.
`{prefix}cf <value>` - Coin flips and decides what you won or lose.
`{prefix}daily` - Claims daily reward.
`{prefix}lb` - Shows leaderboard
`{prefix}loan` - Gives a loan of 500 coins.
`{prefix}returnloan` - Returns loan if taken.
""")
        help_msg = (f'''
Now also supports /slash commands.
For Moderation commands type {prefix}h mod.
For Owner commands type {prefix}h owner.
For More Info Contact <@{owner.id}>.
**Commands:**
`{prefix}help or {prefix}h` - Show this help message.
`{prefix}random <min> <max>` - Gives you a random number.
`{prefix}ping` - checks the ping of bot.
`{prefix}getpfp <user ping>` - Get PFP of ANYONE IN THE DISCORD SERVER.
`{prefix}poll` - Creates a poll in your next message.
`{prefix}userinfo <user>` - Displays info about a user.
`{prefix}suggest <suggestion> - Suggests your idea to the server owner (only workes if suggestions are enabled)`
''')
        if IsEconomy == True:
            help_msg = help_msg + economycommands

        await ctx.send(help_msg)
        return
    elif typ == 'owner':
        prefix = config['prefix']
        owner_id = config['owner_id']
        owner = await bot.fetch_user(owner_id)
        help_msg = (f'''**Commands:**
`{prefix}setstatus` - Custom Status.
`{prefix}clearstatus` - Clears Custom Status.
`{prefix}shutdown` - Shutsdown the bot
For more information contact <@{creator_id}>.
''')
        await ctx.send(help_msg)
        return
    elif typ == 'mod':
        prefix = config['prefix']
        owner_id = config['owner_id']
        owner = await bot.fetch_user(owner_id)
        economycommands = (f'''**Economy Commands**
`{prefix}cset <user> <value>` - sets coins for the given user.
`{prefix}agive <user> <value>` - gives user the specified number of coins.
`{prefix}adelete <user>` - delets a users account.
`{prefix}reset <member>` - Resets account of a member.
''')
        help_msg = (f'''**Commands:**
`{prefix}ban <member> <reason>` - Bans a member from the server.
`{prefix}unban <member>` - Unbans a member from the server.
`{prefix}kick <member>` - Kicks a member from the server.
`{prefix}mute <member>` - Mutes a member of the server.
`{prefix}unmute <member>` - Unmutes a member of the server
`{prefix}setnickname <member>` - Changes nickname of a member.
`{prefix}nickname <value>` - Changes nickname of the bot.
`{prefix}addrole <member> <role>` - Adds a role to a member.
`{prefix}removerole <member> <role>` - Remove role from a member.
`{prefix}createrole <value>` - Creates a role.
`{prefix}deleterole <value>` - Deletes a role.
`{prefix}changerolecolor <valuse> <hex value>` - Changes role colour.
`{prefix}nuke` - deletes messeges of the chat.
`{prefix}reloadresponse` - reloads custom responses.
For More Info Contact <@{owner.id}>.
''')
        if IsEconomy == True:
            help_msg = help_msg + economycommands
            
        await ctx.send(help_msg)


def check_for_updates():
    ACCESS_TOKEN = os.environ.get('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')
    REPO_NAME = 'VA-S-BOT'
    REPO_OWNER = 'DEAMJAVA'
    g = Github(ACCESS_TOKEN)
    repo = g.get_repo(f'{REPO_OWNER}/{REPO_NAME}')
    latest_release = repo.get_latest_release()
    if latest_release.tag_name > current_version:
        print(f'New version {latest_release.tag_name} available!')
        print(f'Download URL: {latest_release.html_url}')
check_for_updates()

def log_to_file(log_message, date_string):
    os.makedirs('Logs', exist_ok=True)
    log_file_path = os.path.join('Logs', f'{date_string}_log.txt')
    with open(log_file_path, 'a', encoding='utf-8') as file:
        file.write(log_message + '\n')

@bot.event
async def on_message(message):
    if config['log'] == True:

        now = datetime.now()
        date_string = now.strftime('%Y-%m-%d')
        time_string = now.strftime('%H-%M-%S')

        log_message = f'{message.guild.name} > #{message.channel.name} > {time_string} > {message.author.name}: {message.content}'

        os.makedirs('Logs', exist_ok=True)

        log_file_path = os.path.join('Logs', f'{date_string}_log.txt')
        with open(log_file_path, 'a', encoding='utf-8') as file:
            file.write(log_message + '\n')

            for attachment in message.attachments:
                file_ext = attachment.filename.split('.')[-1].lower()
                if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'zip', 'rar', 'ico', 'txt']:
                    file_name = f'{message.guild.name}_#{message.channel.name}_{time_string}_{message.author.name}_{attachment.filename}'
                    file_path = os.path.join('Logs', file_name)
                    await attachment.save(file_path)
                    file.write(f'{message.guild.name} > #{message.channel.name} > {time_string} > {message.author.name}: {attachment.filename} > {attachment.url}\n')

            for attachment in message.embeds:
                if attachment.type == 'video':
                    file.write(f'#{message.channel.name} > {time_string} > {message.author.name}: {attachment.video.url}\n')
                elif attachment.type == 'file':
                    file_ext = attachment.filename.split('.')[-1].lower()
                    if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'zip', 'rar', 'ico']:
                        file_name = f'{message.guild.name}_#{message.channel.name}_{time_string}_{message.author.name}_{attachment.filename}'
                        file_path = os.path.join('Logs', file_name)
                        await attachment.save(file_path)
                        file.write(f'{message.guild.name} > #{message.channel.name} > {time_string} > {message.author.name}: {attachment.filename} > {attachment.url}\n')

            if message.attachments or message.embeds:
                file.write('\n')

        def check_message(message, keywords, caps):
            content = message.content if caps else message.content.lower()
            
            pattern = r'\b(?:' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'
            
            matches = re.findall(pattern, content)
            
            return len(matches) == len(keywords)

        words = message.content.lower().split()

        for key, response_data in responses.items():
            keywords = response_data['keywords']
            response = response_data['response']
            caps = response_data.get('caps', False)

            if response_data.get('type', 'any') == "all":
                if check_message(message, keywords, caps):
                    await message.channel.send(response)
                    break
            else:
                if any((keyword in message.content) if caps else (keyword.lower() in message.content.lower()) for
                       keyword in keywords):
                    await message.channel.send(response)
                    break

    await bot.process_commands(message)

@bot.event
async def on_member_update(before, after):
    if config['log'] == True:
        if before.roles != after.roles:
            now = datetime.now()
            date_string = now.strftime('%Y-%m-%d')
            time_string = now.strftime('%H-%M-%S')
            removed_roles = [role for role in before.roles if role not in after.roles]
            added_roles = [role for role in after.roles if role not in before.roles]

            log_message = f'{after.guild.name} > {time_string} > {after.name} roles updated. '

            if removed_roles:
                log_message += f"Removed roles: {', '.join([role.name for role in removed_roles])}. "

            if added_roles:
                log_message += f"Added roles: {', '.join([role.name for role in added_roles])}. "

            if not (added_roles or removed_roles):
                log_message += "No changes in roles."

        if before.name != after.name:
            now = datetime.now()
            date_string = now.strftime('%Y-%m-%d')
            time_string = now.strftime('%H-%M-%S')
            log_message = f'{after.name} username updated. Before: {before.name}, After: {after.name}'
            await log_to_file(log_message, date_string)


@bot.event
async def on_voice_state_update(member, before, after):
    if config['log'] == True:
        if before.channel != after.channel:
            now = datetime.now()
            date_string = now.strftime('%Y-%m-%d')
            time_string = now.strftime('%H-%M-%S')
            if before.channel is None:
                log_message = f'{member.guild.name} > {time_string} > {member.name} joined {after.channel.name}'
            elif after.channel is None:
                log_message = f'{member.guild.name} > {time_string} > {member.name} left {before.channel.name}'
            else:
                log_message = f'{member.guild.name} > {time_string} > {member.name} moved from {before.channel.name} to {after.channel.name}'
            log_to_file(log_message, date_string)


if str(config['plugins']) == True:
    if not os.path.exists('plugins'):
        os.makedirs('plugins')
    plugin_files = [f for f in os.listdir('plugins') if os.path.isfile(os.path.join('plugins', f))]
    globals_dict = globals()
    for plugin_file in plugin_files:
        if plugin_file.endswith(".py"):
            plugin_path = os.path.join(plugins_folder, plugin_file)
            with open(plugin_path) as f:
                code = compile(f.read(), plugin_path, 'exec')
                exec(code, globals_dict)

try:
    bot.run(config['bot_token'])
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        code = """
import os
import time
time.sleep(5)
os.system("python main.py")
"""
        with open("restart.py",'w') as f:
            f.write(code)
        print("Restarting")
        bot.close()
        os.system("python restart.py")
    else:
        raise e    
finally:
    print("Restarting")
    bot.close()
    os.system("python restart.py")
