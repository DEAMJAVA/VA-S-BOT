current_version = 'V10.0'
current_config_format = '16'
plugins_folder = 'plugins'
creator_id = '938059286054072371'
api = 'http://192.9.183.164:25041'
TIMER_FILE = 'time.r'

libraries = """
aiohttp==3.9.3
aiosignal==1.3.1
attrs==23.2.0
blinker==1.7.0
certifi==2024.2.2
cffi==1.16.0
googletrans==4.0.0-rc1
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
cryptography==42.0.5
Deprecated==1.2.14
Flask==3.0.2
frozenlist==1.4.1
idna==3.6
itsdangerous==2.1.2
Jinja2==3.1.3
MarkupSafe==2.1.5
mpmath==1.3.0
multidict==6.0.5
py-cord==2.6.0
pycparser==2.22
PyGithub==2.3.0
PyJWT==2.8.0
PyNaCl==1.5.0
pytz==2024.1
requests==2.31.0
sympy==1.12
typing_extensions==4.10.0
urllib3==2.2.1
Werkzeug==3.0.1
wrapt==1.16.0
yarl==1.9.4
googletrans==4.0.0rc1
"""

# Imports
import os

try:
    import subprocess
    import textwrap
    import pickle
    import atexit
    import signal
    import logging
    import sys
    import re
    import discord
    import json
    import random as rand
    import time
    import asyncio
    import aiohttp
    import pytz
    import calendar
    import traceback
    import requests
    import urllib.request
    import importlib.util
    from discord import Option
    from googletrans import Translator
    from datetime import datetime, timedelta, timezone
    from github import Github, RateLimitExceededException, GithubException
    from discord import Status
    from discord.ext import commands, tasks
    from sympy import symbols, Eq, solve
    from difflib import get_close_matches
except Exception as e:
    print(e)
    with open('libraries.txt', 'w') as f:
        f.write(libraries)
    os.system('pip install -r libraries.txt')
    exit()
#Startup
log = logging.info
logw = logging.warning
logerr = logging.error
logc = logging.critical
loge = logging.exception


# Create Config if not exist
if not os.path.isfile('BotConfig.json'):
    log('No config file found creating BotConfig.json')
    INPUT_PREFIX = input('What do you want the bot prefix to be? \n')
    INPUT_BOT_GROUP_NAME = input(
        "What do you want the bot group name to be (default role perms will be created on this name)\n")
    INPUT_BOT_TOKEN = input('Enter bot token. \n')
    INPUT_OWNER_ID = input("Enter owner's ID.\n")
    INPUT_OWNER_NAME = input("Enter owner's name.\n")

    QUESTION = input("Enable economy? (YES/NO)\n")
    if QUESTION.lower() == 'yes':
        ENABLE_ECONOMY = True
        INPUT_WIN_PROB = int(input("Enter win probability for coinflip.\n")) / 100
        INPUT_INTEREST_RATE = int(input("Enter interest rate for loan.\n")) / 100
        INPUT_DAILY_REWARD_RANGE = input("Enter daily reward range\n").split()
        INPUT_DAILY_REWARD_RANGE_MIN = INPUT_DAILY_REWARD_RANGE[0]
        INPUT_DAILY_REWARD_RANGE_MAX = INPUT_DAILY_REWARD_RANGE[1]
    else:
        ENABLE_ECONOMY = False
        INPUT_DAILY_REWARD_RANGE_MIN = 0
        INPUT_DAILY_REWARD_RANGE_MAX = 0
        INPUT_WIN_PROB = None
        INPUT_INTEREST_RATE = None

    QUESTION = input("Does your server need Member count? (YES/NO)\n")
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
    QUESTION = input("ID of role to ping in tickets\n")
    if QUESTION:
        INPUT_TICKET_HANDLER_ID = QUESTION
    else:
        INPUT_TICKET_HANDLER_ID = None

    config = {
        'config_format': current_config_format,
        'prefix': INPUT_PREFIX,
        'bot_token': INPUT_BOT_TOKEN,
        'welcome_channel': INPUT_WELCOME_CHANNEL_ID,
        'owner_id': INPUT_OWNER_ID,
        'owner_name': INPUT_OWNER_NAME,
        'win_prob': INPUT_WIN_PROB,
        'interest_rate': INPUT_INTEREST_RATE,
        'economy_type': 'local',
        'member_count_id': INPUT_MEMBER_COUNT_ID,
        'leave_channel': INPUT_LEAVE_CHANNEL_ID,
        'suggestion_channel': INPUT_SUGGESTION_CHANNEL_ID,
        'enable_economy': ENABLE_ECONOMY,
        'daily_reward_range-min': int(INPUT_DAILY_REWARD_RANGE_MIN),
        'daily_reward_range-max': int(INPUT_DAILY_REWARD_RANGE_MAX),
        'bot_group_name': INPUT_BOT_GROUP_NAME,
        'ticket_handler': INPUT_TICKET_HANDLER_ID,
        'check_for_updates': True,
        'chatbot': False,
        'plugins': False,
        'log': INPUT_LOG,
    }
    with open('BotConfig.json', 'w') as f:
        f.write(json.dumps(config, indent=4, ensure_ascii=False, separators=(',', ': ')) + '\n')

# Load the config
with open('BotConfig.json') as f:
    config = json.load(f)

logging.basicConfig(level=logging.INFO,
                    format=f"[{config['bot_group_name']} | %(asctime)s | %(levelname)s]: %(message)s")
logger = logging.getLogger()  # Get the root logger
# Define the file handler to log to a file
file_handler = logging.FileHandler('botrunlog.txt')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(f"[{config['bot_group_name']} | %(asctime)s | %(levelname)s]: %(message)s"))
logger.addHandler(file_handler)

bot = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all())

if config['config_format'] != current_config_format:
    logw('Config file is outdated! Please Regenerate config')

SUPPORTED_LANGUAGES = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian', 'az': 'Azerbaijani',
    'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
    'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh-cn': 'Chinese (Simplified)', 'zh-tw': 'Chinese (Traditional)',
    'co': 'Corsican',
    'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish', 'nl': 'Dutch', 'en': 'English', 'eo': 'Esperanto',
    'et': 'Estonian',
    'tl': 'Filipino', 'fi': 'Finnish', 'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian',
    'de': 'German',
    'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian', 'iw': 'Hebrew',
    'hi': 'Hindi',
    'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish',
    'it': 'Italian',
    'ja': 'Japanese', 'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh', 'km': 'Khmer', 'rw': 'Kinyarwanda',
    'ko': 'Korean',
    'ku': 'Kurdish (Kurmanji)', 'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian',
    'lb': 'Luxembourgish',
    'mk': 'Macedonian', 'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori',
    'mr': 'Marathi',
    'mn': 'Mongolian', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'no': 'Norwegian', 'or': 'Odia (Oriya)',
    'ps': 'Pashto',
    'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian',
    'sm': 'Samoan',
    'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona', 'sd': 'Sindhi', 'si': 'Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili', 'sv': 'Swedish',
    'tg': 'Tajik',
    'ta': 'Tamil', 'tt': 'Tatar', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish', 'tk': 'Turkmen', 'uk': 'Ukrainian',
    'ur': 'Urdu', 'ug': 'Uyghur', 'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish',
    'yo': 'Yoruba', 'zu': 'Zulu'
}

# Extra Starting Stuff
IsEconomy: any = config['enable_economy']


def logcommand(message, command):
    if config['log']:
        now = datetime.now()
        date_string = now.strftime('%Y-%m-%d')
        time_string = now.strftime('%H-%M-%S')
        log_message = f'{message.guild.name} > #{message.channel.name} > {time_string} > {message.author.name} used the slash command: {command}'

        os.makedirs('Logs', exist_ok=True)

        log_file_path = os.path.join('Logs', f'{date_string}_log.txt')
        with open(log_file_path, 'a') as file:
            file.write(log_message + '\n')


OWNER_PERMS_GROUP = config['bot_group_name'] + '.' + 'owner'
MOD_PERMS_GROUP = config['bot_group_name'] + '.' + 'mod'
MEMBER_PERMS_GROUP = config['bot_group_name'] + '.' + 'member'


class CreateTicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)  # Set timeout to None to keep the view persistent
        self.bot = bot

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.primary, emoji="🎟️",
                       custom_id="create_ticket_button")
    async def create_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        await handle_ticket_creation(interaction, self.bot)


class CloseTicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)  # Set timeout to None to keep the view persistent
        self.bot = bot

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒",
                       custom_id="close_ticket_button")
    async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        await handle_ticket_closure(interaction, self.bot)


class CloseTicketRequestView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Request to Close Ticket", style=discord.ButtonStyle.primary, emoji="🔒",
                       custom_id="close_request_button")
    async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        await handle_ticket_closure_request(interaction, self.bot)


class DeleteTicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)  # Set timeout to None to keep the view persistent
        self.bot = bot

    @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.danger, emoji="🗑️",
                       custom_id="delete_ticket_button")
    async def delete_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        try:
            await interaction.channel.delete()
        except Exception as e:
            logerr(f"Error while deleting ticket: {e}")
            await interaction.followup.send("An error occurred while deleting the ticket. Please try again later.",
                                            ephemeral=True)


@bot.event
async def on_ready():
    if config['plugins']:
        if not os.path.exists(plugins_folder):
            os.makedirs(plugins_folder)

        for filename in os.listdir(plugins_folder):
            if filename.startswith('on_ready_') and filename.endswith('.ext'):
                log(f'Loading on ready extension {filename}')
                filepath = os.path.join(plugins_folder, filename)
                try:
                    with open(filepath, 'r') as file:
                        script = file.read()
                    exec(script)
                    log(f'Loaded: {filename}')
                except Exception as e:
                    logw(f'Failed to load: {filename}: {e}')

    global timers
    timers = load_timers_state()

    for timer_name in timers.keys():
        await bot.loop.create_task(update_timer(timer_name))

    bot.add_view(CreateTicketView(bot))
    bot.add_view(CloseTicketView(bot))
    bot.add_view(DeleteTicketView(bot))
    bot.add_view(CloseTicketRequestView(bot))

    log(f'Logged in as {bot.user} (ID: {bot.user.id})')

    if not bot.guilds:
        client_id = bot.user.id
        logw(
            f'Bot not in any servers \nOAuth link: https://discord.com/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot')

    log('Starting Post Startup Setup')
    for guild in bot.guilds:
        if not any(role.name == OWNER_PERMS_GROUP for role in guild.roles):
            bot_top_role = guild.get_member(bot.user.id).top_role
            log(f'creating owner group in guild {guild}')
            role = await guild.create_role(name=OWNER_PERMS_GROUP)
            await role.edit(position=bot_top_role.position - 1)
    for guild in bot.guilds:
        if not any(role.name == MOD_PERMS_GROUP for role in guild.roles):
            bot_top_role = guild.get_member(bot.user.id).top_role
            log(f'creating mod group in guild {guild}')
            role = await guild.create_role(name=MOD_PERMS_GROUP)
            await role.edit(position=bot_top_role.position - 2)
    for guild in bot.guilds:
        if not any(role.name == MEMBER_PERMS_GROUP for role in guild.roles):
            log(f'creating member group in guild {guild}')
            await guild.create_role(name=MEMBER_PERMS_GROUP)

    for guild in bot.guilds:
        if not any(role.name == "Muted" for role in guild.roles):
            bot_top_role = guild.get_member(bot.user.id).top_role
            log(f'creating muted role in guild {guild}')
            permissions = discord.Permissions(send_messages=False, speak=False)
            mute_role = await guild.create_role(name="Muted", permissions=permissions)
            await mute_role.edit(position=bot_top_role.position - 3)
            for channel in guild.channels:
                log(f'setting muted perms in guild {guild} channel {channel}')
                try:
                    await channel.set_permissions(mute_role, send_messages=False, speak=False)
                except Exception as e:
                    logw(e)

    log('Post Startup Finished!')

    if config['member_count_id'] is not None:
        channel = bot.get_channel(int(config['member_count_id']))
        member_count = len(channel.guild.members)
        await channel.edit(name=f'Members: {member_count}')


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


AUTO_ROLE_DATA_FILE = 'auto_roles.json'

server_roles = {}


def load_roles():
    global server_roles
    if os.path.isfile(AUTO_ROLE_DATA_FILE):
        with open(AUTO_ROLE_DATA_FILE, 'r') as file:
            server_roles = json.load(file)
    else:
        server_roles = {}


load_roles()


def save_roles():
    with open(AUTO_ROLE_DATA_FILE, 'w') as file:
        json.dump(server_roles, file)


@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)
    if guild_id in server_roles:
        roles = server_roles[guild_id]
        for role_id in roles:
            role_object = discord.utils.get(member.guild.roles, id=role_id)
            if role_object is not None:
                await member.add_roles(role_object)

    global placeholders

    if config['welcome_channel'] is not None:
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
                f.write(json.dumps(ex, indent=4, ensure_ascii=False, separators=(',', ': ')) + '\n')

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
    if config['leave_channel'] is not None:
        channel = bot.get_channel(int(config['leave_channel']))
        await channel.send(f'{member.mention} has left the server. Goodbye 😭')

    if config['member_count_id'] is not None:
        channel = bot.get_channel(int(config['member_count_id']))
        member_count = len(channel.guild.members)
        await channel.edit(name=f'Members: {member_count}')


def has_required_perm():
    async def predicate(ctx):
        if not ctx.guild:
            return True
        try:
            owner_group = discord.utils.get(ctx.guild.roles, name=OWNER_PERMS_GROUP)
            owner_id = config['owner_id']
            mod_group = discord.utils.get(ctx.guild.roles, name=MOD_PERMS_GROUP)

            if str(owner_id) != str(ctx.author.id) and str(creator_id) != str(
                    ctx.author.id) and not mod_group in ctx.author.roles and not owner_group in ctx.author.roles:
                await ctx.send("You don't have the required permission to execute this command!")
                return False
        except Exception as e:
            await ctx.send(f'An error occurred: {e}')
        return True

    return commands.check(predicate)


def has_owner_perm():
    async def predicate(ctx):
        owner_group = discord.utils.get(ctx.guild.roles, name=OWNER_PERMS_GROUP)
        owner_id = config['owner_id']

        if str(owner_id) != str(ctx.author.id) and str(creator_id) != str(
                ctx.author.id) and not owner_group in ctx.author.roles:
            await ctx.send("You don't have the required permission to execute this command!")
            return False
        return True

    return commands.check(predicate)


def is_owner():
    async def predicate(ctx):
        owner_id = config['owner_id']

        if str(owner_id) != str(ctx.author.id) and str(creator_id) != str(ctx.author.id):
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
            await ctx.send('muterole not setup yet, use the setupmute command frist')
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
        await save_state_and_exit()
    except:
        save_timers_state()


@bot.slash_command(description="Shutdowns the bot")
@has_owner_perm()
async def shutdown(ctx):
    try:
        await ctx.respond('Shutting down...')
        save_timers_state()
    except:
        save_timers_state()
    logcommand(message=ctx, command="Shutdown")


@has_owner_perm()
@bot.command(name='restart', aliases=['reload'])
async def restart(ctx):
    await ctx.send("Restarting...")
    logw("Restarting bot")
    await restart_bot()


@bot.slash_command(description="Restarts the bot")
@has_owner_perm()
async def restart(ctx):
    logcommand(message=ctx, command="restart")
    await ctx.respond("Restarting...")
    log("Restarting")
    await restart_bot()


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


@bot.command(name='addrole', aliases=['role'])
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
        await guild.create_role(name=role_name, permissions=permissions)
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


@bot.command(name='changerolecolour')
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


if IsEconomy:

    if config['economy_type'] == 'global':
        @bot.command(name='register')
        async def register(ctx):
            finalapi = api + f'/register/{ctx.author.id}'
            apicall = requests.get(finalapi)
            if int(apicall.text) == 0:
                await ctx.send(f"{ctx.author.mention}, you have been registered with a starting balance of 100 coins.")
            elif int(apicall.text) == 1:
                await ctx.send(f"{ctx.author.mention}, you are already registered.")


        @bot.command(name='give')
        async def give(ctx, recipient: discord.Member, amount: int):
            finalapi = api + f'/give/{ctx.author.id}/{recipient.id}/{amount}'
            apicall = requests.get(finalapi)

            if int(apicall.text) == 0:
                await ctx.send(f"{ctx.author.mention}, you must register before giving coins.")
            elif int(apicall.text) == 1:
                await ctx.send(f"{ctx.author.mention}, the recipient must register before receiving coins.")
            elif int(apicall.text) == 2:
                await ctx.send(f"{ctx.author.mention}, you don't have enough coins to give {amount} coins.")
            elif int(apicall.text) == 3:
                await ctx.send(f"{ctx.author.mention} gave {recipient.mention} {amount} coins.")


        @bot.command(name='cf', aliases=['coinflip'])
        async def cf(ctx, bet: str):
            finalapi = api + f'/cf/{ctx.author.id}/{bet}'
            apicall = requests.get(finalapi)

            if apicall.text == '0':
                await ctx.send(f"{ctx.author.mention}, you are not registered.")
            elif apicall.text == '1':
                await ctx.send(f"{ctx.author.mention}, you do not have enough coins.")
            elif apicall.text == '2':
                await ctx.send(f"{ctx.author.mention}, you cant bet a number lower than 1")
            else:
                data = apicall.json()
                await ctx.send(
                    f"{ctx.author.mention}, you {str(data['result'])} Your balance is now {data['balance']} coins.")


        @bot.command(name='bal', aliases=['balance', 'cash'])
        async def bal(ctx):
            finalapi = api + f'/bal/{ctx.author.id}'
            apicall = requests.get(finalapi)

            if apicall.text == '0':
                await ctx.send(f"{ctx.author.mention}, you are not registered.")
            else:
                data = apicall.json()
                await ctx.send(f"{ctx.author.mention}, your balance is {data['bal']} coins.")


        @bot.command(name='lb', aliases=['baltop', 'cashtop'])
        async def lb(ctx):
            finalapi = api + f'/lb'
            apicall = requests.get(finalapi)

            sorted_balances = apicall.json()
            leaderboard = "```"
            leaderboard += "LEADERBOARD\n"
            leaderboard += "-----------\n"
            for i, (user_id, balance) in enumerate(sorted_balances.items()):
                user = await bot.fetch_user(int(user_id))
                leaderboard += f"{i + 1}. {user.name}: {balance} coins\n"
            leaderboard += "```"
            await ctx.send(leaderboard)


        @bot.command(name='reset')
        async def reset(ctx, member: discord.Member):
            finalapi = api + f'/reset/{ctx.author.id}/{member.id}'
            apicall = requests.get(finalapi)

            if apicall.text == '0':
                await ctx.send("You don't have permission to use this command")
            elif apicall.text == '1':
                await ctx.send("This user does not have a account.")
            elif apicall.text == '2':
                await ctx.send(f"{member.display_name}'s account has been reset to 10 coins.")
            else:
                logw(apicall.text)


        @bot.command(name='adelete')
        async def adelete(ctx, member: discord.Member):
            finalapi = api + f'/adelete/{ctx.author.id}/{member.id}'
            apicall = requests.get(finalapi)

            if apicall.text == '0':
                await ctx.send("You don't have permission to use this command")
            elif apicall.text == '1':
                await ctx.send("This user does not have a player account.")
            elif apicall.text == '2':
                await ctx.send(f"{member.display_name}'s account has been deleted.")
            else:
                logw(apicall.text)


        @bot.command(name='agive')
        async def agive(ctx, recipient: discord.Member, amount: int):
            finalapi = api + f'/agive/{ctx.author.id}/{recipient.id}/{amount}'
            apicall = requests.get(finalapi)

            if apicall.text == '0':
                await ctx.send("You don't have permission to use this command")
            elif apicall.text == '1':
                await ctx.send(f"{ctx.author.mention}, the recipient must register before receiving coins.")
            elif apicall.text == '2':
                await ctx.send(f"Gave {amount} coins to {recipient.mention}.")
            else:
                logw(apicall.text)


        @bot.command(name='cset', aliases=['setc', 'coinset', 'setcoin'])
        async def cset(ctx, recipient: discord.Member, amount: int):
            finalapi = api + f'/cset/{ctx.author.id}/{recipient.id}/{amount}'
            apicall = requests.get(finalapi)

            if apicall.text == '0':
                await ctx.send("You don't have permission to use this command")
            elif apicall.text == '1':
                await ctx.send(f"{ctx.author.mention}, the recipient must register before receiving coins.")
            elif apicall.text == '2':
                await ctx.send(f"Set {amount} coins for user {recipient.mention}.")
            else:
                logw(apicall.text)


        @bot.command(name='daily')
        async def daily(ctx):
            finalapi = api + f'/daily/{ctx.author.id}'
            apicall = requests.get(finalapi)

            if apicall.text == '0':
                await ctx.send(f"{ctx.author.mention}, you are not registered.")
            if apicall.text == '1':
                await ctx.send(f"Congratulations {ctx.author.mention}, you claimed your daily reward")
            else:
                data = apicall.json()
                await ctx.send(
                    f"Sorry {ctx.author.mention}, you can claim your daily reward again in {data['hours']} hours, {data['minutes']} minutes, and {data['seconds']} seconds.")


        @bot.command(name='loan')
        async def loan(ctx):
            finalapi = api + f'/loan/{ctx.author.id}'
            apicall = requests.get(finalapi)

            if apicall.text == '0':
                await ctx.send(f"{ctx.author.mention}, you are not registered.")
                return

            elif apicall.text == '1':
                await ctx.send(f"Sorry {ctx.author.mention}, please return your existing loan.")
            elif apicall.text == '2':
                await ctx.send(
                    f"Sorry {ctx.author.mention}, your balance has been reset as you have failed to repay your loan in time.")
            elif apicall.text == '3':
                await ctx.send(
                    f"{ctx.author.mention}, you have taken a loan of 1000 coins. Please repay it within 24 hours.")
            else:
                logw(apicall.text)


        @bot.command(name='returnloan', aliases=['loanreturn'])
        async def returnloan(ctx):
            finalapi = api + f'/returnloan/{ctx.author.id}'
            apicall = requests.get(finalapi)

            if apicall.text == '0':
                await ctx.send(f"{ctx.author.mention}, you are not registered.")
                return
            elif apicall.text == '1':
                await ctx.send(f"{ctx.author.mention}, you do not have any outstanding loan.")
                return
            data = apicall.json()
            if data['type'] == 0:
                await ctx.send(
                    f"{ctx.author.mention}, you don't have enough coins to return {data['total_amount']} coins.")
                return
            elif data['type'] == 1:
                await ctx.send(
                    f"{ctx.author.mention}, you have returned {data['total_amount']} coins, including {data['interest']} "
                    f"coins of interest. Your new balance is {data['balance']} coins.")



    elif config['economy_type'] == 'local':
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
                await ctx.send(
                    f"Congratulations {ctx.author.mention}, you claimed your daily reward of {reward} coins!")
            elif current_time - last_claim_times[user_id] >= 86400:
                last_claim_times[user_id] = current_time
                reward = rand.randint(100, 1000)
                balances[user_id] += reward
                await ctx.send(
                    f"Congratulations {ctx.author.mention}, you claimed your daily reward of {reward} coins!")
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

            await ctx.send(
                f"{ctx.author.mention}, you have taken a loan of {amount} coins. Please repay it within 24 hours.")


        @bot.command(name='returnloan', aliases=['loanreturn'])
        async def returnloan(ctx):
            with open("balances.json", "r") as f:
                balances = json.load(f)
            user_id = str(ctx.author.id)

            if user_id not in balances:
                await ctx.send(f"{ctx.author.mention}, you are not registered.")
                return

            with open('loan_data.json', 'r') as f:
                loan_data = json.load(f)
            if user_id not in loan_data:
                await ctx.send(f"{ctx.author.mention}, you do not have any outstanding loan.")
                return

            amount = loan_data[user_id]['amount']
            trest = float(config['interest_rate'])
            interest = amount * trest
            user_id = str(ctx.author.id)
            total_amount = int(amount + interest)
            if balances[user_id] < total_amount:
                await ctx.send(
                    f"{ctx.author.mention}, you don't have enough coins to return {int(total_amount)} coins.")
                return
            else:
                total_amount = int(amount + interest)
                balances[user_id] -= total_amount

                del loan_data[user_id]
                with open('loan_data.json', 'w') as f:
                    json.dump(loan_data, f)
                with open('balances.json', 'w') as f:
                    json.dump(balances, f)

                await ctx.send(
                    f"{ctx.author.mention}, you have returned {total_amount} coins, including {int(interest)} coins of interest. Your new balance is {balances[user_id]} coins.")
    else:
        logw('invalid economy type. Please set economy type to local or global')


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
    response = check_for_updates()
    await ctx.send(response)


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
                winner = rand.choice(users)
                await ctx.send(
                    f"🥳 Congratulations, {winner.mention}! You won the {prize} giveaway hosted by {author_mention}!")
            else:
                await ctx.send("No one participated in the giveaway. Better luck next time!")


@bot.slash_command(name="giveaway",
                   description="Creates a giveaway \nUseage: giveaway <Time in Minutes> <prize> <custom message ("
                               "optional)>")
@has_required_perm()
async def giveawayslash(ctx, duration: int, prize: str, custom_message: str = None):
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
                winner = rand.choice(users)
                if custom_message is not None:
                    await ctx.send(custom_message)
                    return
                await ctx.send(
                    f"🥳 Congratulations, {winner.mention}! You won the {prize} giveaway hosted by {author_mention}!")
            else:
                await ctx.send("No one participated in the giveaway. Better luck next time!")
    logcommand(message=ctx, command="Giveaway")


@bot.slash_command(description="make the bot say something",
                   integration_types={discord.IntegrationType.guild_install, discord.IntegrationType.user_install})
@has_required_perm()
async def say(ctx, msg: str):
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.respond("Done", ephemeral=True)
        await ctx.respond(msg)
        return
    await ctx.respond("Done", ephemeral=True)
    await ctx.send(msg)
    logcommand(message=ctx, command="say")


tod = bot.create_group(name="tod")


def create_default_files_for_tod():
    default_truths = ["Tell us your biggest fear.", "What's the most embarrassing thing you've ever done?",
                      "Share a secret you've never told anyone."]
    default_dares = ["Do a silly dance for 30 seconds.", "Sing a song in a funny voice.",
                     "Call a random contact in your phone and say something funny."]

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


@tod.command(name='list', description="List the members in the list")
async def list_tod(ctx):
    with open('TruthOrDare.txt', 'r') as file:
        names = file.readlines()

    if names:
        await ctx.respond("List of names:")
        for name in names:
            await ctx.send(name.strip())
    else:
        await ctx.respond("The list is empty.")
    logcommand(message=ctx, command="list")


last_selected_user = None


@tod.command(description="Spins the list")
async def spin(ctx):
    global last_selected_user

    with open('TruthOrDare.txt', 'r') as file:
        names = file.readlines()

    if names:
        # Remove newline characters and the last selected user from the list
        names = [name.strip() for name in names if name.strip() != last_selected_user]

        if not names:
            # If there are no other options, reset to allow selection of the same user
            names = [last_selected_user]

        selected_name = rand.choice(names)
        last_selected_user = selected_name

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
async def user_info(ctx, user: str = None):
    if ctx.guild is None:
        await ctx.send("This command can only be used in a server.")
        return

    member = None
    user_id = None
    if user is not None:
        try:
            user_id = int(user.strip('<@!>'))
            member = ctx.guild.get_member(user_id)
            if member is None:
                member = await bot.fetch_user(user_id)
        except (ValueError, discord.NotFound):
            await ctx.send("User not found.")
            return
    else:
        member = ctx.author

    created_at_utc = member.created_at.astimezone(pytz.UTC)
    utc_now = datetime.now(pytz.UTC)
    account_age = (utc_now - created_at_utc).days

    if isinstance(member, discord.Member):
        roles = ', '.join([role.mention for role in member.roles if role != ctx.guild.default_role])
        if not roles:
            roles = 'The user has no roles'
        server_owner = 'Yes' if ctx.guild.owner_id == member.id else 'No'
    else:
        roles = 'User not in server'
        server_owner = 'User not in server'

    embed = discord.Embed(title=f'User Info - {member.name}', color=0x7289DA)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name='User ID', value=member.id, inline=False)
    embed.add_field(name='Account Age', value=f'{account_age} days', inline=False)
    embed.add_field(name='Roles', value=roles, inline=False)
    embed.add_field(name='Server Owner', value=server_owner, inline=False)

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
    if config['suggestion_channel'] is not None:
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
async def whatisthetime(ctx):
    now = datetime.now()
    y, m, d = now.year, now.month, now.day
    month_name = calendar.month_name[m]
    current_time = now.strftime("%I:%M:%S:%f:%p")[:-3]
    await ctx.respond(f'{month_name} {y} \nCurrent date: {d} \nCurrent time: {current_time}')
    logcommand(message=ctx, command="Time")


@bot.command(name='giveallrole', aliases=['roleall'])
async def giveall(ctx, *, role: discord.Role = None):
    if not role:
        await ctx.send('Please mention the role')
        return

    await ctx.send(f'Giving role: {role.mention} to all members')

    for member in ctx.guild.members:
        if role not in member.roles:
            try:
                await member.add_roles(role)
                log(f'Giving role to {member}')
            except discord.errors.NotFound:
                await ctx.send(f"Member {member} not found.")
            except Exception as e:
                await ctx.send(f"An error occurred: {e}")

    await ctx.send(f'Role {role.mention} has been added to all members')


@bot.command(name='removeall')
async def removeall(ctx, *, role: discord.Role = None):
    if not role:
        await ctx.send('Please mention the role')
        return

    for member in ctx.guild.members:
        try:
            await member.remove_roles(role)
        except discord.Forbidden:
            await ctx.send(f"Missing permissions to remove the {role.mention} role from {member.name}")
        except discord.errors.NotFound:
            await ctx.send(f"Member {member} not found.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    await ctx.send(f'Role {role.mention} has been removed from all members')


@bot.command(name='mc', aliases=['membercount'])
async def mc(ctx):
    member_count = len(ctx.guild.members)
    if int(member_count) == 1:
        await ctx.send(f'This server has only {member_count} member.')
        return
    await ctx.send(f'This server has a total of {member_count} members.')


@bot.slash_command(name='math', description='Performs basic arithmetic operations',
                   integration_types={discord.IntegrationType.guild_install, discord.IntegrationType.user_install})
async def math(ctx, *, expression: str):
    try:
        expression = re.sub(r'[^\d\+\-\*\/\s]', '', expression)
        result = eval(expression)
        await ctx.respond(f"The result is: {result}")
    except Exception as e:
        await ctx.respond(f"An error occurred: {e}")
    logcommand(message=ctx, command="Math")


@bot.slash_command(name='solve-equation', description='Solves simple linear equations')
async def solve_equation(ctx, *, equation: str):
    try:
        equation = re.sub(r'[^\w\s+\-*=/]', '', equation)

        left_expression, right_expression = equation.split('=')

        x = symbols('x')
        left = eval(left_expression, {'x': x})
        right = eval(right_expression, {'x': x})

        equation = Eq(left, right)
        solution = solve(equation)

        await ctx.send(f"The solution is: {solution}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
    logcommand(message=ctx, command="sole-equation")


@is_owner()
@bot.command(name="exec")
async def execu(ctx, *, val: str = None):
    await ctx.message.delete()
    exec(val)


@is_owner()
@bot.command()
async def createfile(ctx):
    if len(ctx.message.attachments) > 0:
        attachment = ctx.message.attachments[0]
        await attachment.save(attachment.filename)
    else:
        return
    await ctx.message.delete()


@is_owner()
@bot.command(name="eval")
async def evalu(ctx, *, val: str = None):
    await ctx.message.delete()
    eval(val)


@is_owner()
@bot.command()
async def inviteall(ctx):
    if ctx.author.id != int(config['owner_id']):
        return
    if isinstance(ctx.channel, discord.DMChannel):
        for guild in bot.guilds:
            invite = await guild.text_channels[0].create_invite(max_age=0, max_uses=0, unique=True)
            await ctx.author.send(f"Invite link for {guild.name}: {invite}")
    else:
        await ctx.message.delete()


@bot.command(name="getsico")
async def get_server_icon(ctx):
    guild = ctx.guild
    icon_url = guild.icon.url
    await ctx.send(icon_url)


@bot.command(name='dm')
async def direct_message(ctx, user: discord.User, *, content: str = ''):
    try:
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                await user.send(content, file=await attachment.to_file())
        else:
            await user.send(content)
        await ctx.send(f"Sent a direct message to {user.name}")
    except discord.Forbidden:
        await ctx.send("Unable to send a direct message. Make sure the user has DMs enabled.")


@bot.command()
async def si(ctx):
    server_info = ctx.guild
    member_count = len(server_info.members)
    server_name = server_info.name
    server_owner = server_info.owner
    text_channel_count = len(server_info.text_channels)
    voice_channel_count = len(server_info.voice_channels)
    category_count = len(server_info.categories)
    role_count = len(server_info.roles)

    embed = discord.Embed(title='Server Information', description=f'{server_name}')
    embed.add_field(name='Member Count', value=f'{member_count}', inline=True)
    embed.add_field(name='Server Owner', value=server_owner, inline=False)
    embed.add_field(name='Text Channel Count', value=f'{text_channel_count}', inline=True)
    embed.add_field(name='Voice Channel Count', value=f'{voice_channel_count}', inline=True)
    embed.add_field(name='Category Count', value=f'{category_count}', inline=True)
    embed.add_field(name='Role Count', value=f'{role_count}', inline=True)
    await ctx.send(embed=embed)


@is_owner()
@bot.command()
async def postjoinsetup(ctx):
    guild = ctx.guild
    bot_top_role = guild.get_member(bot.user.id).top_role
    await ctx.send('Starting Setup!')
    if not any(role.name == OWNER_PERMS_GROUP for role in guild.roles):
        await ctx.send(f'creating owner group')
        role = await guild.create_role(name=OWNER_PERMS_GROUP)
        await role.edit(position=bot_top_role.position - 1)

    if not any(role.name == MOD_PERMS_GROUP for role in guild.roles):
        await ctx.send('creating mod group')
        role = await guild.create_role(name=MOD_PERMS_GROUP)
        await role.edit(position=bot_top_role.position - 2)

    if not any(role.name == MEMBER_PERMS_GROUP for role in guild.roles):
        await ctx.send('creating member group')
        await guild.create_role(name=MEMBER_PERMS_GROUP)

    if not any(role.name == "Muted" for role in guild.roles):
        await ctx.send('creating muted role')
        permissions = discord.Permissions(send_messages=False, speak=False)
        mute_role = await guild.create_role(name="Muted", permissions=permissions)
        await mute_role.edit(position=bot_top_role.position - 3)
        for channel in guild.channels:
            await ctx.send(f'setting up muted permissions for channel {channel}')
            try:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
            except Exception as e:
                logw(e)
    await ctx.send('Setup DONE!')


@bot.command()
@is_owner()
async def setupmute(ctx):
    mute_role = None
    guild = ctx.guild
    bot_top_role = guild.get_member(ctx.bot.user.id).top_role
    if mute_role is None:
        if not any(role.name == "Muted" for role in guild.roles):
            await ctx.send('creating muted role')
            permissions = discord.Permissions(send_messages=False, speak=False)
            mute_role = await guild.create_role(name="Muted", permissions=permissions)
            await mute_role.edit(position=bot_top_role.position - 3)
        else:
            mute_role = discord.utils.get(guild.roles, name='Muted')

    for channel in guild.channels:
        await ctx.send(f'setting up muted permissions for channel {channel}')
        try:
            await channel.set_permissions(mute_role, send_messages=False, speak=False)
        except Exception as e:
            logw(e)


@is_owner()
@bot.command()
async def oauth(ctx):
    client_id = bot.user.id
    await ctx.send(f'https://discord.com/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot')


@has_required_perm()
@bot.command(name='createvote', aliases=['cv'])
async def create_vote(ctx, *options):
    if not options:
        await ctx.send("Please provide options for the vote.")
        return
    if len(options) > 10:
        await ctx.send("You can only provide up to 10 options.")
        return
    vote_message = f"Vote initiated by {ctx.author.mention}:\n"
    for i, option in enumerate(options, 1):
        vote_message += f"{i}. {option}\n"
    vote_message += "\nReact with the corresponding number to vote!"
    vote = await ctx.send(vote_message)
    for i in range(1, len(options) + 1):
        await vote.add_reaction(f"{i}\N{COMBINING ENCLOSING KEYCAP}")


@has_owner_perm()
@bot.command()
async def plugins(ctx):
    if config['plugins']:
        message = '# Plugins:\n'
        plugin_files = [f for f in os.listdir('plugins') if os.path.isfile(os.path.join('plugins', f))]
        for plugin_file in plugin_files:
            if plugin_file.endswith(".py"):
                message = message + "- " + plugin_file + '\n'
        await ctx.send(message)
    else:
        await ctx.send("Plugin system is disabled.")


@has_owner_perm()
@bot.command()
async def pluginsall(ctx):
    if config['plugins']:
        message = '# Plugins:\n'
        plugin_files = [f for f in os.listdir('plugins') if os.path.isfile(os.path.join('plugins', f))]
        for plugin_file in plugin_files:
            message = message + "- " + plugin_file + '\n'
        await ctx.send(message)
    else:
        await ctx.send("Plugin system is disabled.")


@has_owner_perm()
@bot.command()
async def disableplugin(ctx, plugin_name):
    if config['plugins']:
        plugin_path = os.path.join('plugins', plugin_name)
        if os.path.exists(plugin_path) and plugin_name.endswith(".py"):
            os.rename(plugin_path, plugin_path + ".disabled")
            await ctx.send(f"Plugin `{plugin_name}` disabled successfully.")
        else:
            await ctx.send(f"Plugin `{plugin_name}` not found or already disabled. Please restart the bot")
    else:
        await ctx.send("Plugin system is disabled.")


@has_owner_perm()
@bot.command()
async def enableplugin(ctx, plugin_name):
    if config['plugins']:
        disabled_plugin_path = os.path.join('plugins', plugin_name + ".disabled")
        if os.path.exists(disabled_plugin_path):
            enabled_plugin_path = os.path.join('plugins', plugin_name)
            os.rename(disabled_plugin_path, enabled_plugin_path)
            await ctx.send(f"Plugin `{plugin_name}` enabled successfully. Please restart the bot")
        else:
            await ctx.send(f"Plugin `{plugin_name}` not found or already enabled.")
    else:
        await ctx.send("Plugin system is disabled.")


@has_required_perm()
@bot.command(name="roles")
async def rolelist(ctx, user: discord.Member = None):
    if user is not None:
        roles = user.roles[1:]  # Exclude @everyone role
        if not roles:
            await ctx.send(f"{user.display_name} has no roles.")
            return
        role_list = "\n".join([str(role) for role in reversed(roles)])
        await ctx.send(f"Roles of {user.display_name}:\n{role_list}")
    else:
        role_list = ''
        for role in reversed(ctx.guild.roles):
            if role.name != "@everyone":
                role_list += '\n' + str(role)
        if role_list == '':
            msg = 'There are no roles in this server.'
        else:
            msg = "List of all the roles in the server:" + role_list
        await ctx.send(msg)


if config['chatbot']:
    datapath = 'chatbotdata.json'
    if not os.path.exists(datapath):
        try:
            req = requests.get(api + "/getchatbotdata")
            data = req.json()
        except:
            data = {
                'questions': [

                ]
            }
        with open(datapath, "w") as f:
            json.dump(data, f, indent=2)


    def loadknowledgebase(filepath: str):
        with open(filepath, 'r') as file:
            data: dict = json.load(file)
        return data


    def saveknowledgebase(filepath: str, data: dict):
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=2)


    def findbestmatch(question: str, questions: list[str]):
        matches: list = get_close_matches(question, questions, n=1, cutoff=0.55)
        return matches[0] if matches else None


    def getanswerforguestion(question: str, knowledge_base: dict):
        for q in knowledge_base['questions']:
            if q['question'] == question:
                return q['answer']
        return


    @bot.command(name='chatbot', aliases=['cb', 'b'])
    async def chat_bot(ctx, *, query: str):
        knowledge_base: dict = loadknowledgebase(datapath)
        inp = query
        best_match: str | None = findbestmatch(inp, [q['question'] for q in knowledge_base['questions']])
        if best_match:
            answer: str = getanswerforguestion(best_match, knowledge_base)
            await ctx.send(f'{answer}')
        else:
            await ctx.send("I don't know the answer. Please provide an answer or type 'skip' to skip:")

            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel

            try:
                new_answer_message = await bot.wait_for('message', check=check, timeout=60)
                new_answer = new_answer_message.content.strip()
                if new_answer.lower() != "skip":
                    knowledge_base['questions'].append({'question': inp, 'answer': new_answer})
                    saveknowledgebase(datapath, knowledge_base)
                    await ctx.send('Your answer has been recorded. Thank you!')
                else:
                    await ctx.send('Answer skipped.')
            except asyncio.TimeoutError:
                await ctx.send('You took too long to respond. Answer recording canceled.')


async def handle_ticket_creation(interaction, bot):
    guild = interaction.guild
    category = discord.utils.get(guild.categories, name="Tickets")
    if not category:
        category = await guild.create_category(name="Tickets")

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),  # Deny access to @everyone
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    existing_channels = [channel for channel in category.channels if
                         channel.name == f"ticket-{interaction.user.name}"]
    if existing_channels:
        try:
            await interaction.response.send_message("You already have an open ticket.", ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send("You already have an open ticket.", ephemeral=True)
        return

    try:
        channel = await category.create_text_channel(f'ticket-{interaction.user.name}', overwrites=overwrites)
        msg = f"Your ticket has been created at {channel.mention}. A staff member will assist you shortly."
        await channel.send(f"Ticket opened by <@{interaction.user.id}>. A staff member will assist you shortly.")
        if config['ticket_handler'] is not None:
            role = config['ticket_handler']
            await channel.send(f'<@&{role}>')
        try:
            await interaction.response.send_message(msg, ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send(msg, ephemeral=True)

        # Add CloseTicketView to the ticket channel
        view = CloseTicketRequestView(bot)
        await channel.send("Click the button below to close this ticket.", view=view)
    except discord.HTTPException as e:
        try:
            await interaction.response.send_message(
                "An error occurred while creating the ticket channel. Please try again later.", ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send(
                "An error occurred while creating the ticket channel. Please try again later.", ephemeral=True)
        loge("HTTPException while creating ticket channel")


async def handle_ticket_closure_request(interaction, bot):
    if not interaction.channel.name.startswith('ticket-'):
        try:
            await interaction.response.send_message('This command can only be used in a ticket channel.',
                                                    ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send('This command can only be used in a ticket channel.', ephemeral=True)
        return
    if interaction.custom_id == 'close_request_button':
        view = CloseTicketView(interaction)
        await interaction.channel.send(f'{interaction.user.mention} has requested ticket closure request', view=view)
        try:
            await interaction.response.send_message("Your request to close the ticket has been sent to moderators.",
                                                    ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send("Your request to close the ticket has been sent to moderators.",
                                            ephemeral=True)


async def handle_ticket_closure(interaction, bot):
    if not interaction.channel.name.startswith('ticket-'):
        try:
            await interaction.response.send_message('This command can only be used in a ticket channel.',
                                                    ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send('This command can only be used in a ticket channel.', ephemeral=True)
        return

    if not interaction.user.guild_permissions.administrator:
        try:
            await interaction.response.send_message('You do not have permission to close tickets.', ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send('You do not have permission to close tickets.', ephemeral=True)
        return

    try:
        if interaction.custom_id == 'close_ticket_button':
            await interaction.response.send_message('Archiving ticket...')
            await interaction.channel.send(f"{interaction.user.mention} has closed this ticket.")

            archive_category = discord.utils.get(interaction.guild.categories, name="Archived Tickets")
            if not archive_category:
                archive_category = await interaction.guild.create_category(name="Archived Tickets")

            # Remove user's access from the channel and revoke permissions from everyone
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                # Deny access to @everyone
                interaction.user: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            await interaction.channel.edit(category=archive_category, overwrites=overwrites)
            await interaction.followup.send("Ticket archived successfully.")

            # Add DeleteTicketView to the archived ticket channel for staff
            view = DeleteTicketView(bot)
            await interaction.channel.send("Click the button below to delete this ticket.", view=view)

    except Exception as e:
        loge(f"Error while closing ticket: {e}")
        try:
            await interaction.followup.send("An error occurred while archiving the ticket. Please try again later.")
        except discord.errors.NotFound:
            pass


async def handle_ticket_deletion(interaction):
    if not interaction.channel.name.startswith('ticket-'):
        try:
            await interaction.response.send_message('This command can only be used in a ticket channel.',
                                                    ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send('This command can only be used in a ticket channel.', ephemeral=True)
        return

    try:
        await interaction.channel.delete()
    except Exception as e:
        logerr(f"Error while deleting ticket: {e}")
        try:
            await interaction.followup.send("An error occurred while deleting the ticket. Please try again later.")
        except discord.errors.NotFound:
            pass


async def send_close_request(user, ticket_channel):
    close_request_channel = ticket_channel
    if not close_request_channel:
        loge("Close request channel not found.")
        return

    embed = discord.Embed(
        title=f"Close Request from {user.name}#{user.discriminator}",
        description=f"User {user.mention} has requested closure of their ticket in {ticket_channel.mention}.",
        color=discord.Color.blurple()
    )
    await close_request_channel.send(embed=embed)


ticket_commands = bot.create_group(name='ticket')


@ticket_commands.command(name='setup-ticket-system', description='Sets up the ticket system in a specified channel.')
@has_required_perm()
async def setup_ticket_system(ctx, message=None):
    channel = ctx.channel
    if message is None:
        message = "Click the button below to create a ticket."
    await channel.send(message, view=CreateTicketView(bot))
    await ctx.respond(content=f'Ticket system setup in {channel.mention}', ephemeral=True)
    logcommand(message=ctx, command="setup-ticket-system")


@ticket_commands.command(name='send-close-request', description='Send a close request button in the current channel.')
async def send_close_request(ctx):
    view = CloseTicketView(ctx)
    await ctx.channel.send(f"Ticket closure request by {ctx.user.mention}", view=view)
    await ctx.respond("Close request button sent.", ephemeral=True)
    logcommand(message=ctx, command="send-close-request")


@ticket_commands.command(name='add', description='Add a user to the current ticket.')
@has_required_perm()
async def ticket_add(ctx: discord.ApplicationContext, user: discord.Member):
    if not ctx.channel.name.startswith('ticket-'):
        await ctx.respond('This command can only be used in a ticket channel.', ephemeral=True)
        return

    overwrite = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    await ctx.channel.set_permissions(user, overwrite=overwrite)
    await ctx.respond(f"{user.mention} has been added to the ticket.", ephemeral=True)
    await ctx.channel.send(f"{user.mention} has been added to the ticket by an administrator.")
    logcommand(message=ctx, command="ticket add")


@ticket_commands.command(name='remove', description='Add a user to the current ticket.')
@has_required_perm()
async def ticket_add(ctx: discord.ApplicationContext, user: discord.Member):
    if not ctx.channel.name.startswith('ticket-'):
        await ctx.respond('This command can only be used in a ticket channel.', ephemeral=True)
        return

    overwrite = discord.PermissionOverwrite(read_messages=False, send_messages=False, view_channel=False)
    await ctx.channel.set_permissions(user, overwrite=overwrite)
    await ctx.respond(f"{user.mention} has been removed from the ticket.", ephemeral=True)
    await ctx.channel.send(f"{user.mention} has been removed from the ticket by an administrator.")
    logcommand(message=ctx, command="ticket remove")


@ticket_commands.command(name='close')
@has_required_perm()
async def ticket_force_close(ctx):
    if not ctx.channel.name.startswith('ticket-'):
        await ctx.respond('This command can only be used in a ticket channel.', ephemeral=True)
        return

    archive_category = discord.utils.get(ctx.guild.categories, name="Archived Tickets")
    if not archive_category:
        archive_category = await ctx.guild.create_category(name="Archived Tickets")

    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.user: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    await ctx.channel.edit(category=archive_category, overwrites=overwrites)
    await ctx.respond('Ticket archived successfully.')


@ticket_commands.command(name='delete')
@has_required_perm()
async def ticket_force_close(ctx):
    if not ctx.channel.name.startswith('ticket-'):
        await ctx.respond('This command can only be used in a ticket channel.', ephemeral=True)
        return

    await ctx.channel.delete()


@ticket_commands.command(name='close-all')
@has_required_perm()
async def ticket_force_close_all(ctx):
    ticket_category = discord.utils.get(ctx.guild.categories, name="Tickets")
    if not ticket_category:
        ticket_category = await ctx.guild.create_category(name="Tickets")

    archive_category = discord.utils.get(ctx.guild.categories, name="Archived Tickets")
    if not archive_category:
        archive_category = await ctx.guild.create_category(name="Archived Tickets")

    if not ticket_category.channels:
        await ctx.send('No tickets found!')
        return

    for channel in ticket_category.channels:
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        await channel.edit(category=archive_category, overwrites=overwrites)

    await ctx.respond('Tickets archived successfully.')


@ticket_commands.command(name='delete-all')
@has_required_perm()
async def ticket_force_delete_all(ctx):
    archive_category = discord.utils.get(ctx.guild.categories, name="Archived Tickets")
    if not archive_category:
        archive_category = await ctx.guild.create_category(name="Archived Tickets")

    if not archive_category.channels:
        await ctx.respond('No tickets found!')
        return

    for channel in archive_category.channels:
        await channel.delete()

    await ctx.respond('Tickets deleted successfully.')


afk_file = 'afk_users.json'

if os.path.exists(afk_file):
    with open(afk_file, 'r') as f:
        afk_users = json.load(f)
else:
    afk_users = {}


@bot.command()
async def afk(ctx, *, message="AFK"):
    afk_users[str(ctx.author.id)] = {
        "message": message,
        "time": datetime.now().isoformat(),
        "mentions": []
    }
    with open(afk_file, 'w') as f:
        json.dump(afk_users, f, indent=4)
    await ctx.send(f"{ctx.author.mention} is now AFK: {message}")


timers = {}


def save_timers_state():
    save_data = {name: {'remaining_time': info['remaining_time'], 'start_time': info['start_time']}
                 for name, info in timers.items()}

    with open(TIMER_FILE, 'wb') as f:
        pickle.dump(save_data, f)


def load_timers_state():
    try:
        with open(TIMER_FILE, 'rb') as f:
            save_data = pickle.load(f)
            return {name: {'remaining_time': info['remaining_time'], 'start_time': info['start_time'], 'ctx': None,
                           'initiator': None}
                    for name, info in save_data.items()}
    except (FileNotFoundError, EOFError):
        return {}
    except Exception as e:
        print(f"Error loading timers state: {e}")
        return {}


@bot.command(name='starttimer', aliases=['timer'])
async def start_timer(ctx, duration_str: str, *, timer_name: str = None):
    if timer_name is None:
        timer_name = f"{ctx.author.name}-{ctx.guild.name}-{ctx.channel.name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if timer_name in timers:
        await ctx.send(f"Timer '{timer_name}' is already running.")
        return

    duration_seconds = parse_duration(duration_str)
    if duration_seconds is None:
        await ctx.send("Invalid time format. Use `<number>w|d|h|m|s`.")
        return

    start_time = datetime.now(timezone.utc)

    timers[timer_name] = {
        'remaining_time': duration_seconds,
        'start_time': start_time,
        'ctx': ctx,
        'initiator': ctx.author.id
    }

    await ctx.send(f"Timer '{timer_name}' started for {format_duration(duration_seconds)}.")
    await bot.loop.create_task(update_timer(timer_name))


@bot.command(name='stoptimer')
async def stop_timer(ctx, timer_name: str):
    if timer_name in timers:
        timers.pop(timer_name)
        await ctx.send(f"Timer '{timer_name}' stopped.")
    else:
        await ctx.send(f"Timer '{timer_name}' is not running.")


@bot.command(name='listtimers')
async def list_timers(ctx):
    if timers:
        timer_list = "\n".join([f"{name}: {format_duration(info['remaining_time'])}" for name, info in timers.items()])
        await ctx.send(f"Active timers:\n{timer_list}")
    else:
        await ctx.send("No timers are currently running.")


async def update_timer(timer_name):
    await asyncio.sleep(timers[timer_name]['remaining_time'])

    if timer_name in timers:
        initiator_id = timers[timer_name]['initiator']
        initiator = bot.get_user(initiator_id)
        if initiator:
            await timers[timer_name]['ctx'].send(f"<@{initiator_id}> Your timer '{timer_name}' has ended!")
        timers.pop(timer_name)
        save_timers_state()


def parse_duration(duration_str):
    total_seconds = 0
    duration_regex = re.compile(r'(?P<amount>\d+)\s*(?P<unit>[wdhms])', re.IGNORECASE)
    matches = duration_regex.finditer(duration_str)
    for match in matches:
        amount = int(match.group('amount'))
        unit = match.group('unit').lower()
        if unit == 'w':
            total_seconds += amount * 7 * 24 * 3600
        elif unit == 'd':
            total_seconds += amount * 24 * 3600
        elif unit == 'h':
            total_seconds += amount * 3600
        elif unit == 'm':
            total_seconds += amount * 60
        elif unit == 's':
            total_seconds += amount
    return total_seconds


def format_duration(seconds):
    intervals = (
        ('w', 7 * 24 * 3600),
        ('d', 24 * 3600),
        ('h', 3600),
        ('m', 60),
        ('s', 1)
    )

    result = []
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            result.append(f"{value}{name}")
    return ' '.join(result) or '0s'


@bot.command(name='infotimer')
async def info_timer(ctx, timer_name: str):
    if timer_name in timers:
        remaining_time = timers[timer_name]['remaining_time']
        await ctx.send(f"Timer '{timer_name}' - Time remaining: {format_duration(remaining_time)}")
    else:
        await ctx.send(f"Timer '{timer_name}' is not running.")


@bot.command()
@has_required_perm()
async def hide(ctx):
    try:
        everyone_role = ctx.guild.default_role
        channel = ctx.channel
        await channel.set_permissions(everyone_role, view_channel=False)
        confirmation_msg = await ctx.send(f'{ctx.author.mention}, this channel has been hidden.')
        await confirmation_msg.delete(delay=5)
    except discord.Forbidden:
        await ctx.send("I don't have permission to modify channel permissions.", delete_after=5)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to hide the channel: {e}", delete_after=5)


@bot.command()
@has_required_perm()
async def unhide(ctx):
    try:
        everyone_role = ctx.guild.default_role
        channel = ctx.channel
        await channel.set_permissions(everyone_role, view_channel=True)
        confirmation_msg = await ctx.send(f'{ctx.author.mention}, this channel has been unhidden.')
        await confirmation_msg.delete(delay=5)
    except discord.Forbidden:
        await ctx.send("I don't have permission to modify channel permissions.", delete_after=5)
    except discord.HTTPException as e:
        await ctx.send(f"Failed to unhide the channel: {e}", delete_after=5)


@bot.command(name="sync")
async def sync_commands(ctx):
    await ctx.send("Syncing.....")
    await bot.sync_commands()
    await ctx.send("Sync complete")


@bot.command(name='ch')
@has_required_perm()
async def manage_channel(ctx, action: str, *args):
    if action in ['create', 'vcreate']:
        if len(args) < 1:
            await ctx.send(f"Usage: !ch:{action}:<channel_name>[:<channel_category>][:<force_create_category>]")
            return

        channel_name = args[0]
        channel_category = args[1] if len(args) > 1 else None
        force_create_category = len(args) > 2

        if channel_category:
            category = discord.utils.get(ctx.guild.categories, name=channel_category)

            if category and not force_create_category:
                if action == 'create':
                    await ctx.guild.create_text_channel(channel_name, category=category)
                elif action == 'vcreate':
                    await ctx.guild.create_voice_channel(channel_name, category=category)
                await ctx.send(f'Channel {channel_name} created in existing category {channel_category}.')
            else:
                if category is None or force_create_category:
                    category = await ctx.guild.create_category(channel_category)
                    await ctx.send(f'New category {channel_category} created.')

                if action == 'create':
                    await ctx.guild.create_text_channel(channel_name, category=category)
                elif action == 'vcreate':
                    await ctx.guild.create_voice_channel(channel_name, category=category)
                await ctx.send(f'Channel {channel_name} created in category {channel_category}.')
        else:
            if action == 'create':
                await ctx.guild.create_text_channel(channel_name)
            elif action == 'vcreate':
                await ctx.guild.create_voice_channel(channel_name)
            await ctx.send(f'Channel {channel_name} created without a category.')

    elif action == 'rename':
        if len(args) != 1:
            await ctx.send("Usage: !ch:rename:<new_name>")
            return

        new_name = args[0]
        channel = ctx.channel

        await channel.edit(name=new_name)
        await ctx.send(f'Channel renamed to {new_name}.')

    elif action == 'delete':

        channel = ctx.channel

        await channel.delete()

    elif action == 'deleteall':

        for channel in ctx.guild.channels:
            try:
                await channel.delete()
            except Exception as e:
                logw(e)

    else:
        await ctx.send("Unknown action. Use 'create', 'vcreate', 'rename', 'delete', or 'deleteall'.")


translator = Translator()


@bot.command(name='trans')
async def translate(ctx, *, text: str = None):
    if text:
        # Translate the provided text
        try:
            translated = translator.translate(text, dest='en')
            if translated and translated.text:
                await ctx.send(translated.text)
            else:
                await ctx.send('Translation failed. Please try again.')
        except Exception as e:
            await ctx.send(f'Error: {str(e)}')
    elif ctx.message.reference:
        # Translate the replied-to message
        try:
            referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            text_to_translate = referenced_message.content
            translated = translator.translate(text_to_translate, dest='en')
            if translated and translated.text:
                await ctx.send(f'Translated: {translated.text}')
            else:
                await ctx.send('Translation failed. Please try again.')
        except Exception as e:
            await ctx.send(f'Error: {str(e)}')
    else:
        await ctx.send('Please provide text to translate or reply to a message with `.trans`.')


user_language_settings = {}


@bot.command(name='translang')
async def set_translation_language(ctx, language: str = None):
    if language.lower() == 'none':
        if ctx.author.id in user_language_settings:
            del user_language_settings[ctx.author.id]
        await ctx.send("Default translation language disabled.")
    else:
        language_code = language.lower()
        if language_code in SUPPORTED_LANGUAGES:
            user_language_settings[ctx.author.id] = language_code
            await ctx.send(f"Default translation language set to '{SUPPORTED_LANGUAGES[language_code]}'")
        else:
            await ctx.send(f"Invalid language. Please choose from supported languages or 'none'.")


@bot.command(name='supported_languages', aliases=['langs', 'languages'])
async def show_supported_languages(ctx):
    languages_list = "\n".join([f"`{lang_code}` - {lang_name}" for lang_code, lang_name in SUPPORTED_LANGUAGES.items()])
    await ctx.send(f"Supported Languages:\n{languages_list}")


if 'dev' in current_version:
    @is_owner()
    @bot.command()
    async def pullupdate(ctx):
        url = api + "/get_updated_script"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(__file__, 'w', encoding='utf-8') as script_file:
                    script_file.write(response.text)
                await ctx.send("Update successful! Please restart the bot...")
            else:
                await ctx.send(f"Failed to update. Status code: {response.status_code}")
        except Exception as e:
            await ctx.send(f"Failed to update. Error: {e}")


@bot.command(name='autoroleadd')
@has_required_perm()
async def autoroleadd(ctx, role: discord.Role):
    guild_id = ctx.guild.id
    if guild_id not in server_roles:
        server_roles[guild_id] = []
    if role.id not in server_roles[guild_id]:
        server_roles[guild_id].append(role.id)
        save_roles()
        await ctx.send(f'Role {role.mention} added to auto-roles for this server.')
    else:
        await ctx.send(f'Role {role.mention} is already in the auto-roles list.')


@bot.command(name='autoroleremove')
@has_required_perm()
async def autoroleremove(ctx, role: discord.Role):
    guild_id = ctx.guild.id
    if guild_id in server_roles and role.id in server_roles[guild_id]:
        server_roles[guild_id].remove(role.id)
        save_roles()
        await ctx.send(f'Role {role.mention} removed from auto-roles for this server.')
    else:
        await ctx.send(f'Role {role.mention} is not in the auto-roles list.')


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
`{prefix}suggest <suggestion> - Suggests your idea to the server owner (only works if suggestions are enabled)`
`{prefix}afk` - Marks you as afk.
`{prefix}membercount` - pretty self explanatory.
`{prefix}si` - Shows server information.
`{prefix}trans` [text] - translates a text to english.
`{prefix}translang` <lang> - after selecting a language ever message that user send would be translated by the bot to that language.
''')
        if IsEconomy:
            help_msg = help_msg + economycommands

        await ctx.send(help_msg)
        return
    elif typ == 'owner':
        prefix = config['prefix']
        help_msg = (f'''**Commands:**
`{prefix}setstatus` - Custom Status.
`{prefix}clearstatus` - Clears Custom Status.
`{prefix}shutdown` - Shutsdown the bot.
`{prefix}postjoinsetup` - Sets up a few things for the bot to work properly in the server (bot owner only).
`{prefix}oauth` - generates a OAuth link for inviting the bot (bot owner only).
`{prefix}plugins` - shows all usable plugins.
`{prefix}pluginsall` - shows all plugins including disabled ones or non-plugin files.
`{prefix}disableplugin <plugin name>` - Disables a plugin.
`{prefix}enableplugin <plugin name>` - Enables a plugin if disabled.
`{prefix}setupmute` - sets up the Mute role. 
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
`{prefix}unmute <member>` - Un-mutes a member of the server
`{prefix}setnickname <member>` - Changes nickname of a member.
`{prefix}nickname <value>` - Changes nickname of the bot.
`{prefix}addrole <member> <role>` - Adds a role to a member.
`{prefix}removerole <member> <role>` - Remove role from a member.
`{prefix}createrole <value>` - Creates a role.
`{prefix}deleterole <value>` - Deletes a role.
`{prefix}changerolecolor <values> <hex value>` - Changes role colour.
`{prefix}clear` - deletes messages of the chat.
`{prefix}reloadresponse` - reloads custom responses.
`{prefix}roleall <role mention>` - gives all members a role.
`{prefix}removeall <role mention>` - removes a role from all members.
`{prefix}roles [user]` - shows all the roles in server or roles a user has.
`{prefix}hide` - hides a channel.
`{prefix}unhide` - unhides a channel.
For More Info Contact <@{owner.id}>.
''')
        if IsEconomy:
            help_msg = help_msg + economycommands

        await ctx.send(help_msg)


def check_for_updates():
    try:
        global current_version
        ACCESS_TOKEN = os.environ.get('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')
        REPO_NAME = 'VA-S-BOT'
        REPO_OWNER = 'DEAMJAVA'
        g = Github(ACCESS_TOKEN)
        repo = g.get_repo(f'{REPO_OWNER}/{REPO_NAME}')
        state = "Latest"
        devbuild = False

        release = repo.get_latest_release()
        latest_release = repo.get_latest_release().tag_name

        latest_release = latest_release.strip('V')

        current_version_number = current_version.strip('V')

        if '-' in current_version_number:
            current_version_number = current_version_number.split('-')[0]
            devbuild = True

        if float(latest_release) > float(current_version_number):
            outdated = True
            state = "Outdated"
            logw(f'New version {latest_release} available!')
            logw(f'Download URL: {release.html_url}')
        else:
            outdated = False
        if devbuild:
            state = state + " Development Build"

        message = f"Running Current Version: {current_version} {state}"
        if outdated:
            message = message + f'\nNew version {latest_release} available! \nDownload the Latest version at: {release.html_url}'
        return message
    except RateLimitExceededException:
        logw('GitHub API rate limit exceeded, unable to check for updates at this time')
        return 'GitHub API rate limit exceeded, unable to check for updates at this time'
    except GithubException as e:
        logw(f'Failed to check for updates due to GitHub error: {e}')
        return f'Failed to check for updates due to GitHub error: {e}'
    except Exception as e:
        logw(f'Failed to check for updates due to an unexpected error: {e}')
        return f'Failed to check for updates due to an unexpected error: {e}'


if config['check_for_updates']:
    log(check_for_updates())


def update_code(server_url):
    try:
        with urllib.request.urlopen(server_url) as response:
            updated_script = response.read()

        temp_file = "temp_script.py"
        with open(temp_file, 'wb') as file:
            file.write(updated_script)

        os.replace(temp_file, __file__)

        print("Script updated successfully.")

        python = sys.executable
        subprocess.Popen([python, __file__])
        sys.exit()

    except Exception as e:
        print(f"Error updating script: {e}")


def log_to_file(log_message, date_string):
    os.makedirs('Logs', exist_ok=True)
    log_file_path = os.path.join('Logs', f'{date_string}_log.txt')
    with open(log_file_path, 'a', encoding='utf-8') as file:
        file.write(log_message + '\n')


try:
    with open("responses.json", "r") as f:
        responses = json.load(f)
except FileNotFoundError:
    responses = {}
    with open("responses.json", "w") as f:
        json.dump(responses, f)


async def check_message(message, keywords, caps):
    content = message.content if caps else message.content.lower()
    pattern = r'<@![0-9]+>|' + '|'.join(re.escape(keyword) for keyword in keywords)
    matches = re.findall(pattern, content)

    return len(matches) == len(keywords)


# Function to process responses based on keywords
async def process_responses(message, responses):
    for key, response_data in responses.items():
        keywords = response_data['keywords']
        response = response_data['response']
        caps = response_data.get('caps', False)

        if response_data.get('type', 'any') == "all":
            if await check_message(message, keywords, caps):
                await message.channel.send(response)
                break
        else:
            if any((keyword in message.content) if caps else (keyword.lower() in message.content.lower()) for keyword in
                   keywords):
                await message.channel.send(response)
                break


@bot.event
async def on_message(message):

    if not message.content.startswith(config['prefix']):
        if message.author == bot.user:
            return
        if message.author.id in user_language_settings:
            target_lang = user_language_settings[message.author.id]
            if target_lang != 'none':
                try:
                    translated = translator.translate(message.content, dest=target_lang)
                    await message.reply(f"[Translated to {SUPPORTED_LANGUAGES[target_lang]}]: {translated.text}")
                except Exception as e:
                    await message.channel.send(f"Translation failed: {str(e)}")

    user_id_str = str(message.author.id)

    if user_id_str in afk_users:
        afk_data = afk_users.pop(user_id_str)
        with open(afk_file, 'w') as f:
            json.dump(afk_users, f, indent=4)

        afk_start_time = datetime.fromisoformat(afk_data['time'])
        afk_duration = datetime.now() - afk_start_time

        # Function to convert timedelta to a human-readable format
        def format_timedelta(td):
            seconds = int(td.total_seconds())
            periods = [
                ('day', 60 * 60 * 24),
                ('hour', 60 * 60),
                ('minute', 60),
                ('second', 1)
            ]
            parts = []
            for period_name, period_seconds in periods:
                if seconds > period_seconds or period_name == 'second':
                    period_value, seconds = divmod(seconds, period_seconds)
                    if period_value == 1:
                        parts.append(f"{period_value} {period_name}")
                    elif period_value > 1:
                        parts.append(f"{period_value} {period_name}s")
            return ", ".join(parts)

        afk_duration_str = format_timedelta(afk_duration)
        mention_count = len(afk_data['mentions'])

        mention_details = "\n".join([
            f"{mention['author']} in {mention['channel']}" for mention in afk_data['mentions']
        ]) if mention_count > 0 else "No mentions."

        await message.channel.send(
            f"{message.author.mention} is no longer AFK. You were AFK for {afk_duration_str}.\n"
            f"You were mentioned {mention_count} times:\n{mention_details}"
        )

    if message.mentions:
        for mention in message.mentions:
            if str(mention.id) in afk_users:
                afk_message = afk_users[str(mention.id)]["message"]
                afk_users[str(mention.id)]["mentions"].append({
                    "author": str(message.author),
                    "channel": str(message.channel)
                })
                with open(afk_file, 'w') as f:
                    json.dump(afk_users, f, indent=4)
                await message.channel.send(f"{mention.name} is AFK: {afk_message}")

    await process_responses(message, responses)

    if config['log']:

        now = datetime.now()
        date_string = now.strftime('%Y-%m-%d')
        time_string = now.strftime('%H-%M-%S')

        if message.content is None:
            msg = ''
        else:
            msg = message.content

        if isinstance(message.channel, discord.DMChannel):
            recipient_name = message.channel.recipient.name if message.channel.recipient else "Unknown"
            log_message = f"[DM] {message.author} > {recipient_name} > {time_string}: {msg}"
        else:
            log_message = f'{message.guild.name} > #{message.channel.name} > {time_string} > {message.author.name}: {msg}'

        os.makedirs('Logs', exist_ok=True)

        log_file_path = os.path.join('Logs', f'{date_string}_log.txt')
        with open(log_file_path, 'a', encoding='utf-8') as file:
            file.write(log_message + '\n')

            for attachment in message.attachments:
                file_ext = attachment.filename.split('.')[-1].lower()
                if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'zip', 'rar', 'ico',
                                'txt']:
                    file_name = f'{message.guild.name}_#{message.channel.name}_{time_string}_{message.author.name}_{attachment.filename}'
                    file_path = os.path.join('Logs', file_name)
                    await attachment.save(file_path)
                    file.write(
                        f'{message.guild.name} > #{message.channel.name} > {time_string} > {message.author.name}: {attachment.filename} > {attachment.url}\n')

            for attachment in message.embeds:
                if attachment.type == 'video':
                    file.write(
                        f'#{message.channel.name} > {time_string} > {message.author.name}: {attachment.video.url}\n')
                elif attachment.type == 'file':
                    file_ext = attachment.filename.split('.')[-1].lower()
                    if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'zip', 'rar',
                                    'ico']:
                        file_name = f'{message.guild.name}_#{message.channel.name}_{time_string}_{message.author.name}_{attachment.filename}'
                        file_path = os.path.join('Logs', file_name)
                        await attachment.save(file_path)
                        file.write(
                            f'{message.guild.name} > #{message.channel.name} > {time_string} > {message.author.name}: {attachment.filename} > {attachment.url}\n')
            for embed in message.embeds:
                log_message += f"\nEmbed: {embed.title if embed.title else ''}"
                log_message += f"\nDescription: {embed.description if embed.description else ''}"
                for field in embed.fields:
                    log_message += f"\nField - Name: {field.name if field.name else ''}, Value: {field.value if field.value else ''}"
                log_message += "\n"
                file.write(log_message)

            if message.attachments or message.embeds:
                file.write('\n')

    if config['plugins']:
        for filename in os.listdir(plugins_folder):
            if filename.startswith('on_message_') and filename.endswith('.ext'):
                log(f'Loading on message extension {filename}')
                filepath = os.path.join(plugins_folder, filename)
                try:
                    with open(filepath, 'r') as file:
                        script = file.read()

                    exec(f"async def plugin_func(bot, message):\n{textwrap.indent(script, '    ')}")
                    await locals()['plugin_func'](bot, message)
                    log(f'Successfully executed: {filename}')
                except Exception as e:
                    logw(f'Failed to execute {filename}: {e}')

    await bot.process_commands(message)


@bot.event
async def on_member_update(before, after):
    if config['log']:
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

            log_to_file(log_message, date_string)

        if before.name != after.name:
            now = datetime.now()
            date_string = now.strftime('%Y-%m-%d')
            time_string = now.strftime('%H-%M-%S')
            log_message = f'{after.name} username updated. Before: {before.name}, After: {after.name}'
            log_to_file(log_message, date_string)


@bot.event
async def on_voice_state_update(member, before, after):
    if config['log']:
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


def create_restart_script():
    filename = os.path.basename(__file__)
    script_content = f"""\
import os
import sys
import time

def restart_bot():
    \"\"\"Function to restart the bot\"\"\"
    python = sys.executable
    os.execl(python, python, "{filename}")

if __name__ == "__main__":
    time.sleep(2)  # Give it some time before restarting
    restart_bot()
"""
    with open("restart_script.py", "w") as f:
        f.write(script_content)
    log("Restart script created.")


if config['plugins']:
    if not os.path.exists('plugins'):
        os.makedirs('plugins')
    plugin_files = [f for f in os.listdir('plugins') if os.path.isfile(os.path.join('plugins', f))]
    globals_dict = globals()
    for plugin_file in plugin_files:
        if plugin_file.endswith(".py"):
            log('Loading: ' + plugin_file)
            plugin_path = os.path.join(plugins_folder, plugin_file)
            with open(plugin_path) as f:
                code = compile(f.read(), plugin_path, 'exec')
                exec(code, globals_dict)


def retry_after_message(t):
    waiting = True
    time_remaining = t
    while waiting:
        time_remaining -= 1
        if time_remaining < 0:
            waiting = False
        if time_remaining > 60:
            timestring = f'{time_remaining / 60:.2f} Minutes'
        else:
            timestring = f'{time_remaining} Seconds'
        logger.info(f'Retrying in {timestring}')
        time.sleep(1)


async def save_state_and_exit():
    if timers:
        save_timers_state()
    logger.info("Bot is shutting down...")
    await bot.close()


async def restart_bot():
    if timers:
        save_timers_state()
    logger.info("Bot is restarting...")
    subprocess.Popen(["python", "restart_script.py"])
    await bot.close()


def signal_handler(sig, frame):
    logger.info(f'Received signal {sig}. Exiting gracefully...')
    asyncio.create_task(save_state_and_exit())


atexit.register(lambda: asyncio.run(save_state_and_exit()))
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# Function to run the bot
def run_bot():
    create_restart_script()
    while True:
        try:
            bot.loop.run_until_complete(bot.start(config['bot_token']))
            logger.info('Bot Closed!')
        except discord.HTTPException as e:
            if e.status == 429:
                headers = e.response.headers
                retry_after = float(headers.get('Retry-After', 0))
                logger.warning(f'Rate limited. Retrying after {retry_after} seconds...')
                retry_after_message(retry_after)
            else:
                logger.error(f'An error occurred: {e}')
        except Exception as e:
            logger.error(f'An unexpected error occurred: {e}')
            break


run_bot()
