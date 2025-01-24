current_version = 'V12.4'
current_config_format = '18'
plugins_folder = 'plugins'
creator_id = '938059286054072371'
api = 'http://192.9.183.164:25041'

libraries = """
aiohappyeyeballs==2.4.4
aiohttp==3.11.11
aiosignal==1.3.2
anyio==4.8.0
asyncio-dgram==2.2.0
attrs==24.3.0
certifi==2024.12.14
cffi==1.17.1
charset-normalizer==3.4.1
cryptography==44.0.0
Deprecated==1.2.15
dnspython==2.7.0
frozenlist==1.5.0
googletrans==4.0.2
h11==0.14.0
h2==4.1.0
hpack==4.0.0
httpcore==1.0.7
httpx==0.28.1
hyperframe==6.0.1
idna==3.10
mcstatus==11.1.1
mpmath==1.3.0
multidict==6.1.0
pillow==11.1.0
propcache==0.2.1
py-cord==2.6.1
pycparser==2.22
PyGithub==2.5.0
PyJWT==2.10.1
PyNaCl==1.5.0
pytz==2024.2
requests==2.32.3
setuptools==75.7.0
sniffio==1.3.1
sympy==1.13.3
typing_extensions==4.12.2
urllib3==2.3.0
wrapt==1.17.0
yarl==1.18.3
yt-dlp==2024.12.23
"""

try:
    import os
    import inspect
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
    import base64
    import glob
    import importlib.util
    from discord import Option, SelectOption, ui, InputText
    from googletrans import Translator
    from datetime import datetime, timedelta, timezone
    from collections import defaultdict, deque
    from github import Github, RateLimitExceededException, GithubException
    from discord import Status
    from discord.ui import Button, View, Modal, InputText, Select
    from discord.utils import get
    from discord.ext import commands, tasks
    from PIL import Image
    from io import BytesIO
    from sympy import symbols, Eq, solve
    from difflib import get_close_matches

except ModuleNotFoundError as e:
    print(f"Library not found: {e.name}")
    with open('libraries.txt', 'w') as f:
        f.write(libraries)
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'libraries.txt'])
    exit()
except ImportError as e:
    print(f"Import error: {e}")
    exit()
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    exit()

button_configurations = []
button_views = {}

log = logging.info
logw = logging.warning
logerr = logging.error
logc = logging.critical
loge = logging.exception

if not os.path.isfile('BotConfig.json'):
    log('No config file found creating BotConfig.json')
    INPUT_PREFIX = input('What do you want the bot prefix to be? \n')
    INPUT_BOT_GROUP_NAME = input(
        "Enter a bot log prefix name (Eg name of the bot)\n")
    INPUT_BOT_TOKEN = input('Enter bot token. \n')
    INPUT_OWNER_ID = input("Enter owner's ID.\n")

    QUESTION = input("Enable economy? (YES/NO)\n")
    if QUESTION.lower() == 'yes':
        ENABLE_ECONOMY = True
        INPUT_WIN_PROB = int(input("Enter win probability for coinflip.\n")) / 100
        INPUT_INTEREST_RATE = int(input("Enter interest rate for loan.\n")) / 100
        INPUT_DAILY_REWARD_RANGE = input("Enter daily reward range (answer example 100 - 200)\n").split(' - ')
        INPUT_DAILY_REWARD_RANGE_MIN = INPUT_DAILY_REWARD_RANGE[0]
        INPUT_DAILY_REWARD_RANGE_MAX = INPUT_DAILY_REWARD_RANGE[1]
    else:
        ENABLE_ECONOMY = False
        INPUT_DAILY_REWARD_RANGE_MIN = 0
        INPUT_DAILY_REWARD_RANGE_MAX = 0
        INPUT_WIN_PROB = None
        INPUT_INTEREST_RATE = None

    QUESTION = input("Do you want to log server text messages\n")
    if QUESTION.lower() == 'yes':
        INPUT_LOG = True
    else:
        INPUT_LOG = False

    config = {
        'config_format': current_config_format,
        'prefix': INPUT_PREFIX,
        'bot_token': INPUT_BOT_TOKEN,
        'owner_id': INPUT_OWNER_ID,
        'win_prob': INPUT_WIN_PROB,
        'interest_rate': INPUT_INTEREST_RATE,
        'economy_type': 'local',
        'enable_economy': ENABLE_ECONOMY,
        'daily_reward_range-min': int(INPUT_DAILY_REWARD_RANGE_MIN),
        'daily_reward_range-max': int(INPUT_DAILY_REWARD_RANGE_MAX),
        'bot_group_name': INPUT_BOT_GROUP_NAME,
        'check_for_updates': True,
        'timediff': 0,
        'chatbot': False,
        'plugins': False,
        'log': INPUT_LOG,
    }
    with open('BotConfig.json', 'w') as f:
        f.write(json.dumps(config, indent=4, ensure_ascii=False, separators=(',', ': ')) + '\n')

with open('BotConfig.json') as f:
    config = json.load(f)


def create_button(label: str, style: discord.ButtonStyle, custom_id: str, callback=None, emoji=None, disabled=False):
    button = Button(label=label, style=style, custom_id=custom_id, emoji=emoji, disabled=disabled)
    if callback:
        button.callback = callback
    return button


def create_button_view(label: str, style: discord.ButtonStyle, custom_id: str, callback, emoji=None, disabled=False):
    button = Button(label=label, style=style, custom_id=custom_id, emoji=emoji, disabled=disabled)
    if callback:
        button.callback = callback
    view = discord.ui.View(timeout=None)
    view.add_item(button)
    return view


def create_select_view(placeholder: str, options: list[SelectOption], custom_id: str, callback, min_values: int = 1,
                       max_values: int = 1, disabled=False):
    select = discord.ui.Select(placeholder=placeholder, options=options, custom_id=custom_id, min_values=min_values,
                               max_values=max_values, disabled=disabled)
    if callback:
        select.callback = callback
    view = View(timeout=None)
    view.add_item(select)
    return view


def create_modal_view(title: str, inputs: list[InputText], custom_id: str, callback):
    class CustomModal(Modal):
        def __init__(self):
            super().__init__(title=title, custom_id=custom_id)
            for input_field in inputs:
                self.add_item(input_field)

        async def on_submit(self, interaction: discord.Interaction):
            if callback:
                await callback(interaction, self)

    return CustomModal()


def is_trusted(guild, user):
    if server_configs.get(str(guild.id)):
        if server_configs[str(guild.id)].get('antinuke_trustlist'):
            if user.id in server_configs[str(guild.id)]['antinuke_trustlist']:
                return True
    if guild.owner_id == user.id or user.id == creator_id or user.id == bot.user.id:
        return True
    return False


def is_whitelisted(guild, user):
    if server_configs.get(str(guild.id)):
        if server_configs[str(guild.id)].get('antinuke_whitelist'):
            if user.id in server_configs[str(guild.id)]['antinuke_whitelist']:
                return True
    if is_trusted(guild, user):
        return True
    return False


async def handle_member_kick(member, guild, user):
    if server_configs.get(str(guild.id)):
        if not server_configs.get(str(guild.id)).get('antinuke'):
            return
        if not is_whitelisted(guild, user):
            await user.ban()
            if server_configs.get(str(guild.id)).get('antinuke_logs_channel'):
                channel = bot.get_channel(int(server_configs.get(str(guild.id)).get('antinuke_logs_channel')))
                await channel.send(f"**ANTI NUKE TRIGGERD**: Member {member} was kicked by {user}.")

async def handle_member_ban(member, guild, user):
    if server_configs.get(str(guild.id)):
        if not server_configs.get(str(guild.id)).get('antinuke'):
            return
        if not is_whitelisted(guild, user):
            await user.ban()
            if server_configs.get(str(guild.id)).get('antinuke_logs_channel'):
                channel = bot.get_channel(int(server_configs.get(str(guild.id)).get('antinuke_logs_channel')))
                await channel.send(f"**ANTI NUKE TRIGGERD**: Member {member} was banned by {user}.")


runlog_dir = 'runlogs'
os.makedirs(runlog_dir, exist_ok=True)

logging.basicConfig(level=logging.INFO,
                    format=f"[{config['bot_group_name']} | %(asctime)s | %(levelname)s]: %(message)s")
logger = logging.getLogger()
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

IsEconomy: any = config['enable_economy']


def logcommand(message, command):
    if config['log']:
        date_string = ttime().strftime('%Y-%m-%d')
        time_string = ttime().strftime('%H-%M-%S')
        log_message = f'{message.guild.name} > #{message.channel.name} > {time_string} > {message.author.name} used the slash command: {command}'

        os.makedirs('Logs', exist_ok=True)

        log_file_path = os.path.join('Logs', f'{date_string}_log.txt')
        with open(log_file_path, 'a') as file:
            file.write(log_message + '\n')


OWNER_PERMS_GROUP = config['bot_group_name'] + '.' + 'owner'
MOD_PERMS_GROUP = config['bot_group_name'] + '.' + 'mod'
MEMBER_PERMS_GROUP = config['bot_group_name'] + '.' + 'member'


class CreateTicketView(discord.ui.View):
    def __init__(self, bot, button_message="Create Ticket", emoji="🎟️"):
        super().__init__(timeout=None)
        self.bot = bot
        self.button_message = button_message
        self.emoji = emoji

    @discord.ui.button(style=discord.ButtonStyle.primary, custom_id="create_ticket_button")
    async def create_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        await handle_ticket_creation(interaction, self.bot)

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.label = self.button_message
                child.emoji = self.emoji

    def update_button(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.label = self.button_message
                child.emoji = self.emoji


class CloseTicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒",
                       custom_id="close_ticket_button")
    async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        await handle_ticket_closure(interaction, self.bot)



class DeleteTicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
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


class CloseTicketRequestView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Request to Close Ticket", style=discord.ButtonStyle.primary, emoji="🔒",
                       custom_id="close_request_button")
    async def close_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        await handle_ticket_closure(interaction, self.bot)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


AUTO_ROLE_DATA_FILE = 'auto_roles.json'

server_roles = {}
if os.path.isfile(AUTO_ROLE_DATA_FILE):
    with open(AUTO_ROLE_DATA_FILE, 'r') as file:
        server_roles = json.load(file)
else:
    server_roles = {}


def save_roles():
    with open(AUTO_ROLE_DATA_FILE, 'w') as file:
        json.dump(server_roles, file)


def ttime():
    timediff = float(config.get('timediff', 0))
    time = datetime.now().astimezone(timezone(timedelta(hours=+timediff)))
    return time


def replace_placeholders(content, user):
    default_icon_url = "https://cdn.discordapp.com/embed/avatars/0.png"
    try:
        return content.replace("%user%", str(user)) \
            .replace("%username%", user.name) \
            .replace("%userid%", str(user.id)) \
            .replace("%usermention%", user.mention) \
            .replace("%usericon%", user.avatar.url if user.avatar else default_icon_url) \
            .replace("%time%", ttime().strftime('%d-%m-%Y %I:%M:%S %p')) \
            .replace("%servericon%", user.guild.icon.url if user.guild.icon else default_icon_url) \
            .replace("%servername%", str(user.guild.name))
    except Exception as e:
        loge(e.args)


def get_embed(name: str, user):
    embeds = server_configs.get(str(user.guild.id), {}).get('embeds', {})
    if name not in embeds:
        embed_data = {"title": "", "description":name, "color":0, "fields":[], "footer":"", "image":"", "thumbnail":""}
    else:
        embed_data = embeds[name]

    embed = discord.Embed(
        title=replace_placeholders(embed_data.get("title", ""), user),
        description=replace_placeholders(embed_data.get("description", ""), user),
        color=embed_data.get("color", 0x3498db)
    )
    for field in embed_data.get("fields", []):
        embed.add_field(name=replace_placeholders(field["name"], user),
                        value=replace_placeholders(field["value"], user),
                        inline=field.get("inline", False))
    if embed_data.get("footer"):
        embed.set_footer(text=replace_placeholders(embed_data["footer"], user))

    if embed_data.get("image"):
        url = embed_data["image"]
        if url.startswith("%"):
            url = replace_placeholders(embed_data["image"], user)
        embed.set_image(url=url)

    if embed_data.get("thumbnail"):
        url = embed_data["thumbnail"]
        if url.startswith("%"):
            url = replace_placeholders(embed_data["thumbnail"], user)
        embed.set_thumbnail(url=url)
    return embed


server_config_file = 'server_configs.json'


def load_server_configs():
    if os.path.exists(server_config_file):
        with open(server_config_file, 'r') as file:
            return json.load(file)
    else:
        return {}


def save_server_configs(config):
    with open(server_config_file, 'w') as file:
        file.write(json.dumps(config))


server_configs = load_server_configs()

when_bot_ready_functions = []
def when_bot_ready(function):
    when_bot_ready_functions.append(function)
    return function


when_member_join_functions = []
def when_member_join(function):
    when_member_join_functions.append(function)
    return function


@bot.event
async def on_member_join(member):
    for f in when_member_join_functions:
        f(member)
    if str(member.guild.id) in server_roles:
        guild_id = str(member.guild.id)
        for role_id in server_roles[guild_id]:
            role_object: discord.Role = get(member.guild.roles, id=role_id)
            if role_object:
                await member.add_roles(role_object)
            else:
                server_roles[guild_id].remove(role_id)


    server_config = server_configs.get(str(member.guild.id))
    if server_config:
        if server_config.get('member_count_channel'):
            channel = bot.get_channel(int(server_config.get('member_count_channel')))
            if not channel:
                server_configs[str(member.guild.id)]['member_count_channel'] = None
                save_server_configs(server_configs)
            else:
                member_count = len(channel.guild.members)
                await channel.edit(name=f'Members: {member_count}')


    guild: discord.Guild = member.guild
    server_config: dict = server_configs.get(str(guild.id))
    if not server_config:
        return
    channel = bot.get_channel(server_config.get('welcome_channel_id'))
    embed_name = server_config.get('welcome_embed')
    if not channel or not embed_name:
        return

    await channel.send(embed=get_embed(embed_name, member))

when_member_leave_functions = []
def when_member_leave(function):
    when_member_leave_functions.append(function)
    return function

@bot.event
async def on_member_remove(member):
    for f in when_member_leave_functions:
        f(member)
    guild = member.guild
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        if entry.target == member:
            await handle_member_kick(member, guild, entry.user)

    server_config = server_configs.get(str(member.guild.id))
    if server_config:
        if server_config.get('member_count_channel'):
            channel = bot.get_channel(int(server_config.get('member_count_channel')))
            if not channel:
                server_configs[str(member.guild.id)]['member_count_channel'] = None
                save_server_configs(server_configs)
            else:
                member_count = len(channel.guild.members)
                await channel.edit(name=f'Members: {member_count}')


    guild: discord.Guild = member.guild
    server_config: dict = server_configs.get(str(guild.id))
    if not server_config:
        return
    channel = bot.get_channel(server_config.get('leave_channel_id'))
    embed_name = server_config.get('leave_embed')
    if not channel or not embed_name:
        return

    await channel.send(embed=get_embed(embed_name, member))

when_member_ban_functions = []
def when_member_ban(function):
    when_member_ban_functions.append(function)
    return function

@bot.event
async def on_member_ban(guild, member):
    for f in when_member_ban_functions:
        f(guild, member)
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        if entry.target == member:
            await handle_member_ban(member, guild, entry.user)

when_channel_create_functions = []
def when_channel_create(function):
    when_channel_create_functions.append(function)
    return function

@bot.event
async def on_guild_channel_create(channel):
    for f in when_channel_create_functions:
        f(channel)
    guild = channel.guild
    if server_configs.get(str(guild.id)):
        if not server_configs.get(str(guild.id)).get('antinuke'):
            return
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            if not is_whitelisted(guild, entry.user):
                await entry.user.ban()
                if server_configs.get(str(guild.id)).get('antinuke_logs_channel'):
                    channel = bot.get_channel(int(server_configs.get(str(guild.id)).get('antinuke_logs_channel')))
                    await channel.send(f'**ANTI NUKE TRIGGERD**: Channel created: {channel.name} by {entry.user}')


when_channel_delete_functions = []
def when_channel_delete(function):
    when_channel_delete_functions.append(function)
    return function

@bot.event
async def on_guild_channel_delete(channel):
    for f in when_channel_delete_functions:
        f(channel)
    guild = channel.guild
    if server_configs.get(str(guild.id)):
        if not server_configs.get(str(guild.id)).get('antinuke'):
            return
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if not is_whitelisted(guild, entry.user):
                await entry.user.ban()
                if server_configs.get(str(guild.id)).get('antinuke_logs_channel'):
                    channel = bot.get_channel(int(server_configs.get(str(guild.id)).get('antinuke_logs_channel')))
                    await channel.send(f'**ANTI NUKE TRIGGERD**: Channel deleted: {channel.name} by {entry.user}')

when_channel_update_functions = []
def when_channel_update(function):
    when_channel_update_functions.append(function)
    return function

@bot.event
async def on_guild_channel_update(before, after):
    for f in when_channel_update_functions:
        f(before, after)
    guild = before.guild
    if server_configs.get(str(guild.id)):
        if not server_configs.get(str(guild.id)).get('antinuke'):
            return
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_update):
            if not is_whitelisted(guild, entry.user):
                await entry.user.ban()
                if server_configs.get(str(guild.id)).get('antinuke_logs_channel'):
                    channel = bot.get_channel(int(server_configs.get(str(guild.id)).get('antinuke_logs_channel')))
                    await channel.send(f'**ANTI NUKE TRIGGERD**: Channel updated: {before.name} -> {after.name} by {entry.user}')

when_role_create_functions = []
def when_role_create(function):
    when_role_create_functions.append(function)
    return function

@bot.event
async def on_guild_role_create(role):
    for f in when_role_create_functions:
        f(role)
    guild = role.guild
    if server_configs.get(str(guild.id)):
        if not server_configs.get(str(guild.id)).get('antinuke'):
            return
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
            if not is_whitelisted(guild, entry.user):
                await entry.user.ban()
                if server_configs.get(str(guild.id)).get('antinuke_logs_channel'):
                    channel = bot.get_channel(int(server_configs.get(str(guild.id)).get('antinuke_logs_channel')))
                    await channel.send(f'**ANTI NUKE TRIGGERD**: Role created: {role.name} by {entry.user}')

when_role_delete_functions = []
def when_role_delete(function):
    when_role_delete_functions.append(function)
    return function


@bot.event
async def on_guild_role_delete(role):
    for f in when_role_delete_functions:
        f(role)
    guild = role.guild
    if server_configs.get(str(guild.id)):
        if not server_configs.get(str(guild.id)).get('antinuke'):
            return
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
        if not is_whitelisted(guild, entry.user):
            await entry.user.ban()
            if server_configs.get(str(guild.id)).get('antinuke_logs_channel'):
                channel = bot.get_channel(int(server_configs.get(str(guild.id)).get('antinuke_logs_channel')))
                await channel.send(f'**ANTI NUKE TRIGGERD**: Role deleted: {role.name} by {entry.user}')

when_role_update_functions = []
def when_role_update(function):
    when_role_update_functions.append(function)
    return function

@bot.event
async def on_guild_role_update(before, after):
    for f in when_role_update_functions:
        f(before, after)
    guild = before.guild
    if server_configs.get(str(guild.id)):
        if not server_configs.get(str(guild.id)).get('antinuke'):
            return
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_update):
            if not is_whitelisted(guild, entry.user):
                await entry.user.ban()
                if server_configs.get(str(guild.id)).get('antinuke_logs_channel'):
                    channel = bot.get_channel(int(server_configs.get(str(guild.id)).get('antinuke_logs_channel')))
                    await channel.send(f'**ANTI NUKE TRIGGERD**: Role updated: {before.name} -> {after.name} by {entry.user}')


when_guild_update_functions = []
def when_guild_update(function):
    when_guild_update_functions.append(function)
    return function

@bot.event
async def on_guild_update(before, after):
    for f in when_guild_update_functions:
        f(before, after)
    guild = after
    if server_configs.get(str(guild.id)):
        if not server_configs.get(str(guild.id)).get('antinuke'):
            return
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.guild_update):
            await entry.user.ban()
            if server_configs.get(str(guild.id)).get('antinuke_logs_channel'):
                channel = bot.get_channel(int(server_configs.get(str(guild.id)).get('antinuke_logs_channel')))
                await channel.send(f'**ANTI NUKE TRIGGERD**: Guild settings updated by {entry.user}')


def has_required_perm():
    async def predicate(ctx):
        if not ctx.guild:
            await ctx.send("Please use this command in a server!")
            return False
        try:
            guild = ctx.guild
            guild_id = str(ctx.guild.id)
            author_id = ctx.author.id
            if not server_configs.get(guild_id):
                server_configs[guild_id] = {'owners':[], 'authorized_users': []}
                save_server_configs(server_configs)
            if not server_configs[guild_id].get('owners'):
                server_configs[guild_id]['owners'] = []
                save_server_configs(server_configs)
            if not server_configs[guild_id].get('authorized_users'):
                server_configs[guild_id]['authorized_users'] = []
                save_server_configs(server_configs)
            if str(author_id) == config['owner_id']:
                return True
            if author_id == guild.owner_id or author_id in server_configs[guild_id]['owners'] or author_id in server_configs[guild_id]['authorized_users'] or str(author_id) == creator_id:
                return True
        except Exception as e:
            await ctx.send(f'An error occurred: {e}')
        await ctx.send(f"You don't have access to use this command!")
        return False

    return commands.check(predicate)


def has_owner_perm():
    async def predicate(ctx):
        if not ctx.guild:
            await ctx.send("Please use this command in a server!")
            return False
        try:
            guild = ctx.guild
            guild_id = str(ctx.guild.id)
            author_id = ctx.author.id
            if not server_configs.get(guild_id):
                server_configs[guild_id] = {'owners': [], 'authorized_users': []}
                save_server_configs(server_configs)
            if not server_configs[guild_id].get('owners'):
                server_configs[guild_id]['owners'] = []
                save_server_configs(server_configs)
            if str(author_id) == config['owner_id']:
                return True
            if author_id == guild.owner_id or author_id in server_configs[guild_id]['owners'] or str(author_id) == creator_id or str(author_id):
                return True
        except Exception as e:
            await ctx.send(f'An error occurred: {e}')
        await ctx.send(f"You don't have access to use this command!")
        return False

    return commands.check(predicate)


def is_owner():
    async def predicate(ctx):
        owner_id = config['owner_id']
        if str(owner_id) != str(ctx.author.id) and str(creator_id) != str(ctx.author.id):
            await ctx.send(f"You don't have access to use this command!")
            return False
        return True

    return commands.check(predicate)


helps = {}
bot_prefix = config['prefix']
def add_help(category, name, description):
    if not helps.get(category):
        helps[category] = {}
    helps[category][name] = description


@bot.command(name='kick')
@has_required_perm()
async def kick(ctx, member: discord.Member):
    try:
        await member.kick()
        await ctx.send(f"{member.name} has been kicked!")
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')
add_help('Moderation', 'kick <member>', 'kicks a member from the server')


@bot.command(name='ban')
@has_required_perm()
async def ban(ctx, member: discord.Member):
    try:
        await member.ban()
        await ctx.send(f'{member} has been banned from the server.')
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')
add_help('Moderation', 'ban <member>', 'bans a member from the server')


@bot.command(name='unban')
@has_required_perm()
async def unban(ctx, *, name):
    try:
        mention_match = re.match(r"<@!?(\d+)>", name)
        user_id = None
        if mention_match:
            user_id = int(mention_match.group(1))
        async for ban_entry in ctx.guild.bans():
            user = ban_entry.user
            if user_id and user.id == user_id:
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} has been unbanned from the server.')
                return
            elif name.lower() in [f"{user.name}#{user.discriminator}".lower(), user.name.lower()]:
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} has been unbanned from the server.')
                return
        await ctx.send(f'Could not find a banned user with the name: {name}')
    except discord.Forbidden:
        await ctx.send("I don't have permission to unban members.")
    except discord.HTTPException as e:
        await ctx.send(f"An error occurred while unbanning: {e}")
    except Exception as e:
        await ctx.send(f"An unexpected error occurred: {e}")
add_help('Moderation', 'unban <member>', 'unbans a member from the server')


@bot.command(name='mute')
@has_required_perm()
async def mute(ctx, member: discord.Member):
    guild = ctx.guild
    try:
        mute_role = discord.utils.get(guild.roles, name="Muted")
        if not mute_role:
            mute_role = await setupmute(ctx)
        await member.add_roles(mute_role)
        await ctx.send(f"{member.mention} has been muted.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
add_help('Moderation', 'mute <member>', 'mutes a member in the server')


@bot.command(name='unmute')
@has_required_perm()
async def unmute(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    try:
        muted_role = discord.utils.get(guild.roles, name='Muted')
        await member.remove_roles(muted_role)
        await ctx.send(f"{member.mention} has been unmuted.")
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')
add_help('Moderation', 'unmute <member>', 'unmutes a member in the server')


@bot.command(name='shutdown')
@is_owner()
async def shutdown(ctx):
    await ctx.send('Shutting down...')
    await save_state_and_exit()
add_help('Owner', 'shutdown', 'shuts down the bot')


@bot.command(name='status')
@is_owner()
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
        await ctx.send(f'An error occurred: {e}')
add_help('Owner', 'status <status>', 'changes bot status between online, invisible, idle and dnd')


@bot.command(name='setcstatus', aliases=['setstatus', 'customstatus', 'scs'])
@is_owner()
async def setcstatus(ctx, status_type: str, *, status_text: str = ""):
    try:
        status_type = status_type.lower()
        status_text = status_text.strip()

        current_presence = bot.status
        activity = None

        if status_type == "playing":
            activity = discord.Game(name=status_text)
        elif status_type == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=status_text)
        elif status_type == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=status_text)
        elif status_type == "streaming":
            activity = discord.Streaming(name=status_text, url="https://www.twitch.tv/Streaming")
        elif status_type == "competing":
            activity = discord.Activity(type=discord.ActivityType.competing, name=status_text)
        else:
            await ctx.send(
                "Invalid status type. Valid options are `playing`, `listening`, `watching`, `streaming`, `competing`,")
            return

        await bot.change_presence(activity=activity, status=current_presence)
        status_message = f"Status set to: `{status_type.title()}`"
        if status_text:
            status_message += f" `{status_text}`"
        await ctx.send(status_message)

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
add_help('Owner', 'setstatus <playing/listening/watching/streaming/competing> <text>', 'sets custom activity')


@bot.command(name='clearstatus')
@is_owner()
async def clearstatus(ctx):
    try:
        await bot.change_presence(activity=None)
        await ctx.send("Status cleared.")
    except Exception as e:
        await ctx.send('An error occurred: {e}')
add_help('Owner', 'clearstatus', 'Clears bot activity')


@bot.command(name='setnickname')
@has_required_perm()
async def setnickname(ctx, member: discord.Member, *, new_nickname: str):
    try:
        await member.edit(nick=new_nickname)
        await ctx.send(f"Nickname has been changed to {new_nickname}.")
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')
add_help('Moderation', 'setnickname <member> <name>', 'changes nickname of a member')


@bot.command(name='nickname')
@has_required_perm()
async def nickname(ctx, *, new_name: str):
    try:
        await ctx.guild.me.edit(nick=new_name)
        await ctx.send(f"My nickname has been changed to {new_name}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
add_help('Moderation', 'nickname <name>', 'changes nickname of the bot')


@bot.command(name='random')
async def random(ctx, mi=0, ma=10000):
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
add_help('General', 'random [minimum] [maximum]', 'Gives out a random number between the maximum and minimum number. if no values are provided it will generate a random number between 0 and 1000')


@bot.slash_command(name='random',
                   integration_types={discord.IntegrationType.guild_install, discord.IntegrationType.user_install})
async def random_slash(ctx, mi, ma):
    try:
        prefix = config['prefix']
        if mi is None or ma is None or int(mi) >= int(ma) or not isinstance(
                int(mi), int) or not isinstance(int(ma), int):
            await ctx.send(f'Incorrect usage. Please use `{prefix}random [minimum] [maximum]` with integer values.')
            return
        output = rand.randint(int(mi), int(ma))
        await ctx.respond(f'Your random number is: {output}')
    except Exception as e:
        await ctx.respond(f"An error occurred: {e}")


@bot.command(name='addrole', aliases=['role'])
@has_required_perm()
async def addrole(ctx, member: discord.Member, role: discord.Role):
    try:
        await member.add_roles(role)
        await ctx.send(
            f"{member.display_name} has been given the {role.name} role.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
add_help('Moderation', 'addrole <member> <role>', 'gives a role to a member')


@bot.command(name='removerole')
@has_required_perm()
async def removerole(ctx, member: discord.Member, role: discord.Role):
    try:
        await member.remove_roles(role)
        await ctx.send(f"{member.display_name} has had the {role.name} role removed.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
add_help('Moderation', 'removerole <member> <role>', 'removes a role from the member')


@bot.command(name='createrole', aliases=['makerole', 'rolecreate'])
@has_required_perm()
async def createrole(ctx, *, role_name):
    try:
        guild = ctx.guild
        permissions = discord.Permissions(
            send_messages=True,
            read_messages=True)
        await guild.create_role(name=role_name, permissions=permissions)
        await ctx.send(f"Role {role_name} has been created.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
add_help('Moderation', 'createrole <name>', 'creates a role')


@bot.command(name='deleterole', aliases=['roledelete'])
@has_required_perm()
async def deleterole(ctx, *, role_input: str = None):
        if role_input is None:
            return await ctx.send("Please specify a role to delete or use 'all' to delete all roles.")

        if role_input.lower() == "all":
            if not ctx.author.guild_permissions.administrator:
                return await ctx.send("You need administrator permissions to delete all roles.")

            deletable_roles = [r for r in ctx.guild.roles if r != ctx.guild.default_role]
            if not deletable_roles:
                return await ctx.send("No roles available to delete.")

            for role in deletable_roles:
                try:
                    await role.delete()
                except:
                    pass
            return await ctx.send("All deletable roles have been deleted.")

        if len(ctx.message.role_mentions) > 0:
            role = ctx.message.role_mentions[0]
        else:
            roles = [r for r in ctx.guild.roles if r.name == role_input]
            if len(roles) == 0:
                return await ctx.send(f"No roles found with the name '{role_input}'.")
            if len(roles) > 1:
                return await ctx.send(
                    f"Multiple roles found with the name '{role_input}'. Please mention the role to delete."
                )
            role = roles[0]

        if role >= ctx.guild.me.top_role:
            return await ctx.send(
                f"I cannot delete the role `{role.name}` as it is higher than or equal to my top role.")

        await role.delete()
        await ctx.send(f"Role `{role.name}` has been deleted.")
add_help('Moderation', 'deleterole <role>', 'deletes a role from the server')


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
                remaining_time = datetime.fromtimestamp(last_claim_times[user_id] + 86400) - ttime()
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
async def clear(ctx, target=None, amount: int = None):
    await ctx.message.delete()

    def check_message_pin(msg):
        return not msg.pinned

    if target and target.isdigit():
        amount = int(target)
        target = None

    if amount is None:
        amount = float('inf')

    async def limited_purge(check):
        deleted = []
        async for msg in ctx.channel.history():
            if len(deleted) >= amount:
                break
            if check(msg) and not msg.pinned:
                await msg.delete()
                deleted.append(msg)
        return deleted

    if target in ["bots", "bot"]:
        deleted = await limited_purge(lambda msg: msg.author.bot)
    elif target in ["users", "user"]:
        deleted = await limited_purge(lambda msg: not msg.author.bot)
    elif target:
        try:
            member = await commands.MemberConverter().convert(ctx, target)
            deleted = await limited_purge(lambda msg: msg.author == member)
        except commands.BadArgument:
            await ctx.send("User not found.")
            return
    else:
        deleted = await ctx.channel.purge(limit=amount, check=check_message_pin)
    response = f'Cleared {len(deleted)} messages. {f'By {target if target else None}' if target else ''}'
    await ctx.send(response)
add_help('Moderation', 'clear [target] [amount]', 'clears the chat. in a limited amount if provided. clears messages by spesific user if target is provided')


@bot.command(name='clears', aliases=['nukes'])
@has_required_perm()
async def clear(ctx: discord.context, target=None, amount: int = None):
    await ctx.message.delete()

    def check_message_pin(msg):
        return not msg.pinned

    if target and target.isdigit():
        amount = int(target)
        target = None

    if amount is None:
        amount = float('inf')

    async def limited_purge(check):
        deleted = []
        async for msg in ctx.channel.history(limit=1000):
            if len(deleted) >= amount:
                break
            if check(msg) and not msg.pinned:
                await msg.delete()
                deleted.append(msg)
        return deleted

    if target in ["bots", "bot"]:
        deleted = await limited_purge(lambda msg: msg.author.bot)

    elif target in ["users", "user"]:
        deleted = await limited_purge(lambda msg: not msg.author.bot)

    elif target:
        try:
            member = await commands.MemberConverter().convert(ctx, target)

            deleted = await limited_purge(lambda msg: msg.author == member)
        except commands.BadArgument:
            await ctx.send("User not found.", delete_after=5)
            return

    else:
        deleted = await ctx.channel.purge(limit=amount, check=check_message_pin)

    log(f'Silent Deleted {len(deleted)} messages from guild {ctx.guild.name} | Target: {target if target else "All"} | By {ctx.author.name}')
add_help('Moderation', 'clears [target] [amount]', 'basically clear but does not send message after its done')


@bot.command(name='version', aliases=['ver'])
async def version(ctx):
    response = check_for_updates()
    await ctx.send(response)
add_help('General', 'version', 'Tells you the version of the bot and if its outdated')


@bot.command(name='ping')
async def ping(ctx):
    latency = bot.latency
    await ctx.send(f'Pong! Latency: {latency * 1000:.2f}ms')
add_help('General', 'ping', 'checks bot latency')


@bot.command()
@has_required_perm()
async def lock(ctx, *, role: discord.Role = None):
    channel = ctx.channel
    if role is None:
        role = ctx.guild.default_role

    overwrite = channel.overwrites_for(role)
    overwrite.send_messages = False
    await channel.set_permissions(role, overwrite=overwrite)

    await ctx.send(f"{channel.mention} has been locked for {role.mention}.")
add_help('Moderation', 'lock <role>','Locks the channel for the given role. If no role is provided, locks the channel for everyone.')


@bot.command()
@has_required_perm()
async def unlock(ctx, *, role: discord.Role = None):
    channel = ctx.channel
    if role is None:
        role = ctx.guild.default_role

    overwrite = channel.overwrites_for(role)
    overwrite.send_messages = True
    await channel.set_permissions(role, overwrite=overwrite)

    await ctx.send(f"{channel.mention} has been unlocked for {role.mention}.")
add_help('Moderation', 'unlock <role>','Unlocks the channel for the given role. If no role is provided, unlocks the channel for everyone.')


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
add_help('General', 'getpfp [user]', 'dms you your pfp link or the pfp link of the user provided')


@bot.command(name="reloadresponses", aliases=['reloadresponse', 'responsesreload', 'responsereload'])
@is_owner()
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
add_help('Owner', 'reloadresponses', 'reloads the auto resposes config')


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
add_help('General', 'poll', 'adds reaction to the next message you send within the next 20 seconds creating a upvote and downvote')


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
    logcommand(message=ctx, command="say")
    await ctx.respond("Done", ephemeral=True)
    await ctx.send(msg)


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
        names = [name.strip() for name in names if name.strip() != last_selected_user]

        if not names:
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

    created_at_utc = member.created_at.astimezone(timezone.utc)
    utc_now = datetime.now(timezone.utc)
    account_age = (utc_now - created_at_utc).days

    if isinstance(member, discord.Member):
        roles = ', '.join([role.mention for role in member.roles if role != ctx.guild.default_role])
        if not roles:
            roles = 'The user has no roles'
        server_owner = 'Yes' if ctx.guild.owner_id == member.id else 'No'

        joined_at_utc = member.joined_at.astimezone(timezone.utc) if member.joined_at else None
        if joined_at_utc:
            joined_days_ago = (utc_now - joined_at_utc).days
            joined_info = f"Joined: {joined_at_utc.strftime('%d-%m-%Y %I:%M:%S %p')} ({joined_days_ago} days ago)"
        else:
            joined_info = "Joined information not available."
    else:
        roles = 'User not in server'
        server_owner = 'User not in server'
        joined_info = 'User not in server'

    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    embed_color = None
    avg_color = await get_average_color(avatar_url)
    if avg_color:
        embed_color = (avg_color[0] << 16) + (avg_color[1] << 8) + avg_color[2]

    embed = discord.Embed(
        title=f'User Info - {member.name}',
        color=discord.Color(embed_color) if embed_color else discord.Color(0x7289DA)
    )
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name='User ID', value=member.id, inline=False)
    embed.add_field(name='Created On', value=f'{created_at_utc.strftime('%d-%m-%Y %I:%M:%S %p')}', inline=False)
    embed.add_field(name='Account Age', value=f'{account_age} days', inline=False)
    embed.add_field(name='Roles', value=roles, inline=False)
    embed.add_field(name='Server Owner', value=server_owner, inline=False)
    embed.add_field(name='Server Join Date', value=joined_info, inline=False)

    await ctx.send(embed=embed)
add_help('General', 'userinfo <member>', 'gives information about the user')


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
    now = ttime()
    y, m, d = now.year, now.month, now.day
    month_name = calendar.month_name[m]
    current_time = now.strftime("%I:%M:%S:%f:%p")[:-3]
    await ctx.respond(f'{month_name} {y} \nCurrent date: {d} \nCurrent time: {current_time}')
    logcommand(message=ctx, command="Time")
add_help('General', 'time', 'tells you the bots local time')


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
add_help('Moderation', 'roleall <role>', 'gives all server members a role')


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
add_help('Moderation', 'removeall <role>', 'remove removes a role from all server members')


@bot.command(name='mc', aliases=['membercount'])
async def mc(ctx):
    member_count = len(ctx.guild.members)
    if int(member_count) == 1:
        await ctx.send(f'This server has only {member_count} member.')
    else:
        await ctx.send(f'This server has a total of {member_count} members.')
    server_config = server_configs.get(str(ctx.guild.id))
    if server_config:
        if server_config.get('member_count_channel'):
            channel = bot.get_channel(int(server_config.get('member_count_channel')))
            if not channel:
                server_configs[str(ctx.guild.id)]['member_count_channel'] = None
                save_server_configs(server_configs)
            else:
                await channel.edit(name=f'Members: {member_count}')
add_help('General', 'mc', 'tells you the membercount of the server')


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


@bot.command(name='math')
async def math_normal(ctx, *, expression: str):
    try:
        expression = re.sub(r'[^\d\+\-\*\/\s]', '', expression)
        result = eval(expression)
        await ctx.send(f"The result is: {result}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


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
add_help('Owner', 'exec <code>', 'executes some code')


@is_owner()
@bot.command(name="cmd")
async def execcmd(ctx, *, val: str = None):
    await ctx.message.delete()
    os.system(val)
add_help('Owner', 'cmd <command>', 'executes a shell command in the system')


@is_owner()
@bot.command(name='createfile', aliases=['crf'])
async def createfile(ctx):
    if len(ctx.message.attachments) > 0:
        attachment = ctx.message.attachments[0]
        await attachment.save(attachment.filename)

    await ctx.message.delete()
add_help('Owner', 'createfile <attachment>', 'uploades the provided attachment to the bots directory')


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
add_help('Owner', 'inviteall', 'invites you to all the servers the bot is in')


@bot.command(name="getsservericon", aliases=['getsico'])
async def get_server_icon(ctx):
    guild = ctx.guild
    icon_url = guild.icon.url
    await ctx.send(icon_url)
add_help('General', 'getsico', 'gives you the link of the server icon')


@bot.command(name='dm')
@is_owner()
async def direct_message(ctx, user: discord.User, *, content: str = 'Hello!'):
    try:
        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                await user.send(content, file=await attachment.to_file())
        else:
            await user.send(content)
        await ctx.send(f"Sent a direct message to {user.name}")
    except discord.Forbidden:
        await ctx.send("Unable to send a direct message. Make sure the user has DMs enabled.")
add_help('Owner', 'dm <user> <message>', 'Dms a user the provided message')


async def get_average_color(image_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                img_data = await response.read()
                image = Image.open(BytesIO(img_data))
                image = image.resize((50, 50))
                pixels = list(image.getdata())
                avg_color = tuple(sum(c) // len(c) for c in zip(*pixels))
                return avg_color
    return None


@bot.command()
async def si(ctx):
    server_info: discord.Guild = ctx.guild
    member_count = len(server_info.members)
    server_name = server_info.name
    server_owner = server_info.owner.mention
    text_channel_count = len(server_info.text_channels)
    channel_count = len(server_info.channels)
    voice_channel_count = len(server_info.voice_channels)
    category_count = len(server_info.categories)
    verification_level = server_info.verification_level
    stickers = len(server_info.stickers)
    emojis = len(server_info.emojis)
    animated_emojis = len([emoji for emoji in server_info.emojis if emoji.animated])
    static_emojis = emojis - animated_emojis
    boost_count = server_info.premium_subscription_count or 0
    boost_tier = server_info.premium_tier
    role_count = len(server_info.roles)

    creation_date = server_info.created_at
    current_date = datetime.now(timezone.utc)
    age = current_date - creation_date
    age_days = age.days
    server_icon = server_info.icon.url if server_info.icon else None

    embed_color = None
    if server_icon:
        avg_color = await get_average_color(server_icon)
        if avg_color:
            embed_color = (avg_color[0] << 16) + (avg_color[1] << 8) + avg_color[2]

    embed = discord.Embed(
        title='Server Information',
        description=f'{server_name}',
        color=discord.Color(embed_color) if embed_color else discord.Color.default()
    )
    embed.add_field(name='Member Count', value=f'{member_count}', inline=True)
    embed.add_field(name='Server Owner', value=server_owner, inline=True)
    embed.add_field(name='Channel Count', value=f'{channel_count}', inline=True)
    embed.add_field(name='Text Channel Count', value=f'{text_channel_count}', inline=True)
    embed.add_field(name='Voice Channel Count', value=f'{voice_channel_count}', inline=True)
    embed.add_field(name='Category Count', value=f'{category_count}', inline=True)
    embed.add_field(name='Role Count', value=f'{role_count}', inline=True)
    embed.add_field(name='Verification Level', value=f'{verification_level}', inline=True)
    embed.add_field(name='Stickers', value=f'{stickers}/{server_info.sticker_limit}', inline=True)
    embed.add_field(name='Static Emojis', value=f'{static_emojis}/{server_info.emoji_limit}', inline=True)
    embed.add_field(name='Animated Emojis', value=f'{animated_emojis}/{server_info.emoji_limit}', inline=True)
    embed.add_field(name='Boost Level', value=f'{boost_tier}', inline=True)
    embed.add_field(name='Boost Count', value=f'{boost_count}', inline=True)
    embed.set_footer(
        text=f'Date Created: {creation_date.strftime("%d-%m-%Y %I:%M:%S %p")} | Age: {age_days} days | ID: {server_info.id}')
    if server_icon:
        embed.set_thumbnail(url=server_icon)

    await ctx.send(embed=embed)
add_help('General', 'si', 'gives you server information')


async def setupmute(ctx, channel: discord.abc.GuildChannel):
    guild = ctx.guild
    bot_top_role = guild.get_member(ctx.bot.user.id).top_role
    mute_role = discord.utils.get(guild.roles, name="Muted")
    if mute_role is None:
        await ctx.send('Creating muted role...')
        permissions = discord.Permissions(send_messages=False, speak=False)
        mute_role = await guild.create_role(name="Muted", permissions=permissions)
        await mute_role.edit(position=bot_top_role.position - 3)
    if mute_role in channel.overwrites and channel.overwrites[mute_role].send_messages is False and channel.overwrites[
        mute_role].speak is False:
        await ctx.send(f'Muted role is already set up for {channel.mention}.')
        return mute_role
    await ctx.send(f'Setting up muted permissions for {channel.mention}...')
    try:
        if isinstance(channel, discord.TextChannel):
            await channel.set_permissions(mute_role, send_messages=False)
        elif isinstance(channel, discord.VoiceChannel):
            await channel.set_permissions(mute_role, speak=False)
    except Exception as e:
        logw(e)

    return mute_role

@has_required_perm()
@bot.command(name='setupmute')
async def setup_mute_command(ctx, channel = None):
    if not channel:
        channel = str(ctx.channel.id)
    if channel == 'all':
        for channel in ctx.guild.channels:
            await setupmute(ctx, channel)
    else:
        channel = ctx.guild.get_channel(int(channel.strip('<#>')))
        await setupmute(ctx, channel)
add_help('Moderation', 'setupmute', 'sets up the mute role')


@is_owner()
@bot.command()
async def oauth(ctx):
    client_id = bot.user.id
    await ctx.send(f'https://discord.com/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot')
add_help('Owner', 'oauth', 'gives you the authorization link of the bot')


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
add_help('Moderation', 'createvote <options>', 'creates a vote between options')


@has_required_perm()
@bot.command(name="roles")
async def rolelist(ctx, user: discord.Member = None):
    if user is not None:
        roles = user.roles[1:]
        if not roles:
            await ctx.send(f"{user.display_name} has no roles.")
            return
        role_list = "\n - ".join([role.mention for role in reversed(roles)])
        embed = discord.Embed(title=f"**Roles of {user.display_name}**", description=role_list, color=discord.Color.green())
        await ctx.send(embed=embed)
    else:
        role_list = ''
        for role in reversed(ctx.guild.roles):
            if role.name != "@everyone":
                role_list += '\n - ' + role.mention
        if role_list == '':
            embed = discord.Embed(title="There are no roles in this server", color=discord.Color.red())
        else:
            embed = discord.Embed(title="**List of all the roles in the server**", description=role_list, color=discord.Color.green())
        await ctx.send(embed=embed)
add_help('Moderation', 'roles [member]', 'lists all roles in server or the roles of a user')


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


    add_help('General', 'b <message>', 'Talk with chatbot')


ticket_ids = {}
if not os.path.exists('ticket_numbers.json'):
    with open('ticket_numbers.json', 'w') as f:
        json.dump({}, f)

with open('ticket_numbers.json', 'r') as f:
    ticket_ids = json.load(f)


def save_ticket_data():
    with open('ticket_numbers.json', 'w') as f:
        json.dump(ticket_ids, f)

when_ticket_create_functions = []
def when_ticket_create(function):
    when_ticket_create_functions.append(function)
    return function

async def handle_ticket_creation(interaction, bot):
    guild = interaction.guild
    guild_id = str(guild.id)
    user_id = str(interaction.user.id)

    if guild_id not in ticket_ids:
        ticket_ids[guild_id] = {'counter': 1, 'users': {}}

    guild_data = ticket_ids[guild_id]

    if user_id in guild_data['users']:
        channel_id = guild_data['users'][user_id]
        channel = interaction.guild.get_channel(channel_id)

        if channel is None:
            del guild_data['users'][user_id]
        else:
            archived_category_name = "Archived Tickets"
            if channel.category and channel.category.name == archived_category_name:
                del guild_data['users'][user_id]
            else:
                try:
                    await interaction.response.send_message(
                        "You already have an open ticket.", ephemeral=True
                    )
                    return
                except discord.errors.NotFound:
                    await interaction.followup.send(
                        "You already have an open ticket.", ephemeral=True
                    )
                    return


    category = discord.utils.get(guild.categories, name="Tickets")
    if not category:
        category = await guild.create_category(name="Tickets")

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    try:
        ticket_number = guild_data['counter']
        channel_name = f'ticket-{ticket_number}-{interaction.user.name}'
        channel = await category.create_text_channel(channel_name, overwrites=overwrites)

        for f in when_ticket_create_functions:
            f(ticket_number, interaction.user, channel)

        guild_data['users'][user_id] = channel.id
        guild_data['counter'] += 1
        save_ticket_data()

        server_configs = load_server_configs()
        ticket_message = f"Ticket opened by <@{interaction.user.id}>. A staff member will assist you shortly."
        if server_configs.get(str(interaction.guild.id)) is not None:
            if server_configs[str(interaction.guild.id)].get('ticket_message'):
                message = server_configs[str(interaction.guild.id)]['ticket_message']
                ticket_message = replace_placeholders(message, interaction.user)
        await channel.send(ticket_message)


        if server_configs.get(str(interaction.guild.id)) is not None:
            if server_configs[str(interaction.guild.id)].get('ticket_handler'):
                role = server_configs[str(interaction.guild.id)]['ticket_handler']
                await channel.send(f'<@&{role}>')

        msg = f"Your ticket has been created at {channel.mention}. A staff member will assist you shortly."
        try:
            await interaction.response.send_message(msg, ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send(msg, ephemeral=True)

        view = CloseTicketRequestView(bot)
        await channel.send("Click the button below to close this ticket.", view=view)

    except discord.HTTPException as e:
        try:
            await interaction.response.send_message(
                "An error occurred while creating the ticket channel. Please try again later.", ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send(
                "An error occurred while creating the ticket channel. Please try again later.", ephemeral=True)
        loge(f"HTTPException while creating ticket channel: {e}")


async def handle_ticket_closure(interaction, bot):
    guild_id = str(interaction.guild.id)
    user_id = None
    for user, channel_id in ticket_ids[guild_id]['users'].items():
        if interaction.channel.id == channel_id:
            user_id = str(user)
            break

    if not interaction.channel.name.startswith('ticket-'):
        try:
            await interaction.response.send_message('This command can only be used in a ticket channel.',
                                                    ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send('This command can only be used in a ticket channel.', ephemeral=True)
        return
    if not interaction.user.guild_permissions.administrator:
        view = CloseTicketView(interaction)
        await interaction.channel.send(f'{interaction.user.mention} has requested ticket closure request', view=view)
        try:
            await interaction.response.send_message("Your request to close the ticket has been sent to moderators.",
                                                    ephemeral=True)
        except discord.errors.NotFound:
            await interaction.followup.send("Your request to close the ticket has been sent to moderators.",
                                            ephemeral=True)
        return

    try:
        if interaction.custom_id in ['close_ticket_button', 'close_request_button']:
            await interaction.response.send_message('Archiving ticket...')
            await interaction.channel.send(f"{interaction.user.mention} has closed this ticket.")
            ticket_ids[guild_id]['users'].pop(user_id)
            save_ticket_data()
            archive_category = discord.utils.get(interaction.guild.categories, name="Archived Tickets")
            if not archive_category:
                archive_category = await interaction.guild.create_category(name="Archived Tickets")

            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            await interaction.channel.edit(category=archive_category, overwrites=overwrites)
            await interaction.channel.send("Ticket archived successfully.")
            transcript_path = await transcribe_ticket(interaction.channel)
            user = interaction.guild.get_member(int(user_id))
            if user and server_configs.get(str(interaction.guild.id), {}).get('send_ticket_transcripts', False):
                try:
                    with open(transcript_path, "rb") as file:
                        await user.send("Here is the transcript of your ticket:",
                                        file=discord.File(file, filename=os.path.basename(transcript_path)))
                    await interaction.channel.send(f"Transcript has been sent to {user.mention}.")
                except discord.Forbidden:
                    await interaction.channel.send(f"Could not DM {user.mention} the transcript. Please enable DMs.")

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


async def transcribe_ticket(channel):
    guild_folder = f'transcripts/{sanitize_filename(channel.guild.name)}'
    if not os.path.exists(guild_folder):
        os.makedirs(guild_folder)
    transcript = []
    transcript.append(f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Transcript - #{channel.name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #36393f; color: white; padding: 20px; }}
            .message {{ display: flex; align-items: flex-start; margin-bottom: 10px; }}
            .avatar {{ width: 40px; height: 40px; border-radius: 50%; margin-right: 10px; }}
            .content {{ background: #40444b; padding: 10px; border-radius: 8px; max-width: 80%; }}
            .timestamp {{ font-size: 12px; color: #b9bbbe; margin-left: 5px; }}
            .mention {{ color: #7289da; background: rgba(114, 137, 218, 0.1); padding: 2px 4px; border-radius: 4px; }}
            .mention.role {{ color: #faa61a; }}
            .mention.channel {{ color: #44b07b; }}
        </style>
    </head>
    <body>
        <h2>Transcript for #{channel.name}</h2>
        <p>Channel ID: {channel.id}</p>
        <p>Created at: {channel.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr>
    """)
    async for message in channel.history(oldest_first=True):
        timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        avatar_url = message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
        content = format_mentions(message)
        transcript.append(f"""
        <div class="message">
            <img class="avatar" src="{avatar_url}" alt="Avatar">
            <div>
                <strong>{message.author.name}</strong> <span class="timestamp">{timestamp}</span>
                <div class="content">{content}</div>
            </div>
        </div>
        """)
    transcript.append("</body></html>")
    filename = f"{channel.name}-{channel.id}.html"
    file_path = os.path.join(guild_folder, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(transcript))
    return file_path


def format_mentions(message):
    content = message.content
    for user in message.mentions:
        content = content.replace(f"<@{user.id}>", f'<span class="mention">@{user.name}</span>')
    for role in message.role_mentions:
        content = content.replace(f"<@&{role.id}>", f'<span class="mention role">@{role.name}</span>')
    for channel in message.channel_mentions:
        content = content.replace(f"<#{channel.id}>", f'<span class="mention channel">#{channel.name}</span>')
    return content


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
async def setup_ticket_system(ctx, message=None, emoji="🎟️", button_message="Create Ticket"):
    channel = ctx.channel
    if message is None:
        message = "Click the button below to create a ticket."
    view = CreateTicketView(ctx.bot, button_message=button_message, emoji=emoji)
    view.update_button()
    await channel.send(message, view=view)
    await ctx.respond(content=f'Ticket system setup in {channel.mention}', ephemeral=True)
    logcommand(message=ctx, command="setup-ticket-system")


@ticket_commands.command(name='set-ticket-handler', description='Sets the role to ping in tickets')
@has_required_perm()
async def setup_ticket_ping(ctx, role: discord.Role):
    server_id = str(ctx.guild.id)
    if not role:
        await ctx.respond("No role selected please select a role", ephemeral= True)
        return
    if server_id not in server_configs:
        server_configs[server_id] = {}
    server_configs[server_id]['ticket_handler'] = role.id
    save_server_configs(server_configs)
    await ctx.respond("Ticket handler defined successfully", ephemeral=True)
    logcommand(message=ctx, command="setup-ticket-handler")


@ticket_commands.command(name='send-ticket-transcripts', description='toggles weather to send ticket trnscripts to users or not')
@has_required_perm()
async def setup_ticket_transcript(ctx, arg: bool):
    server_id = str(ctx.guild.id)
    server_configs.setdefault(server_id, {})['send_ticket_transcripts'] = arg
    save_server_configs(server_configs)
    await ctx.respond(f"Sending ticket transcripts to users is now {arg}", ephemeral=True)
    logcommand(message=ctx, command="send-ticket-transcripts")


@ticket_commands.command(name='set-ticket-message', description='Sets the message sent in tickets')
@has_required_perm()
async def setup_ticket_message(ctx, message: str):
    server_id = str(ctx.guild.id)
    if server_id not in server_configs:
        server_configs[server_id] = {}
    server_configs[server_id]['ticket_message'] = message
    save_server_configs(server_configs)
    await ctx.respond("Ticket message defined successfully", ephemeral=True)
    logcommand(message=ctx, command="setup-ticket-message")


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
async def ticket_remove(ctx: discord.ApplicationContext, user: discord.Member):
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
    await transcribe_ticket(ctx.channel)


@ticket_commands.command(name='delete')
@has_required_perm()
async def ticket_force_delete(ctx):
    if not ctx.channel.name.startswith('ticket-'):
        await ctx.respond('This command can only be used in a ticket channel.', ephemeral=True)
        return
    channel: discord.TextChannel = ctx.channel
    if not channel.category.name == 'Archived Tickets':
        await ctx.respond('Ticket must be closed first', ephemeral=True)
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
        await transcribe_ticket(ctx.channel)
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

    await ctx.respond('Deleting all tickets')

    for channel in archive_category.channels:
        try:
            await channel.delete()
        except discord.errors.HTTPException as e:
            loge(e)
        except Exception as e:
            log(e.args)

    await ctx.respond('Tickets deleted successfully.')


@ticket_commands.command(name='transcribe-all')
@has_required_perm()
async def transcribe_tickets(ctx: discord.Interaction):
    guild = ctx.guild
    archived_category = discord.utils.get(guild.categories, name="Archived Tickets")

    if not archived_category:
        await ctx.respond("Archived Tickets category not found.")
        return

    if not os.path.exists(f'transcripts/{sanitize_filename(ctx.guild.name)}'):
        os.makedirs(f'transcripts/{sanitize_filename(ctx.guild.name)}')

    await ctx.respond(f"Transcribing tickets")

    for channel in archived_category.text_channels:
        transcript = [f"Transcript for channel: #{channel.name}", f"Channel ID: {channel.id}",
                      f"Created at: {channel.created_at.strftime('%Y-%m-%d %H:%M:%S')}", "=" * 50]

        async for message in channel.history(oldest_first=True):
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            transcript.append(f"[{timestamp}] {message.author.name}: {message.content}")
            transcript.append("-" * 50)

        transcript.append("=" * 50)
        transcript.append(f"End of transcript for channel: #{channel.name}")

        filename = f"{channel.name}-{channel.id}.txt"
        with open(os.path.join('transcripts', sanitize_filename(ctx.guild.name), filename), "w", encoding="utf-8") as f:
            f.write("\n".join(transcript))

    await ctx.respond(f"Transcripts saved for all channels in {archived_category.name}.")
    logcommand(message=ctx, command="transcribe-all")

@ticket_commands.command(name='transcribe')
@has_required_perm()
async def transcribe_ticket_command(ctx, silent: bool = False):
    await transcribe_ticket(ctx.channel)
    if not silent:
        await ctx.channel.send(f"Transcribed ticket {ctx.channel.name}")
    logcommand(message=ctx, command="transcribe")


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
        "time": ttime().isoformat(),
        "mentions": []
    }
    with open(afk_file, 'w') as f:
        json.dump(afk_users, f, indent=4)
    await ctx.send(f"{ctx.author.mention} is now AFK: {message}")
add_help('General', 'afk [reason]', 'Sets you as afk until you send another message')


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
add_help('Moderation', 'hide', 'hides a channel')


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
add_help('Moderation', 'unhide', 'unhides a channel')


@bot.command(name='ch')
@has_required_perm()
async def manage_channel(ctx, action: str, *args):
    if action in ['create', 'vcreate']:
        if len(args) < 1:
            await ctx.send(f"Usage: {bot_prefix}ch:{action}:<channel_name>[:<channel_category>][:<force_create_category>]")
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
add_help('Moderation', 'ch <action>', "Channel actions: 'create', 'vcreate', 'rename', 'delete', or 'deleteall'.")


translator = Translator()


@bot.command(name='trans')
async def translate(ctx, *, text: str = None):
    if text:
        try:
            translated = translator.translate(text, dest='en')
            if translated and translated.text:
                await ctx.send(translated.text)
            else:
                await ctx.send('Translation failed. Please try again.')
        except Exception as e:
            await ctx.send(f'Error: {str(e)}')
    elif ctx.message.reference:
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
add_help('General', 'trans [text]', 'translates given text or reference message')


user_language_settings = {}


@bot.command(name='translang')
async def set_translation_language(ctx: discord.ApplicationContext, language: str = None, user: discord.User = None):
    userid = user.id if user else ctx.author.id
    if language.lower() in ['none', 'off', 'null']:
        if userid in user_language_settings:
            del user_language_settings[userid]
        await ctx.send("Default translation language disabled.")
    else:
        language_code = language.lower()
        if language_code in SUPPORTED_LANGUAGES:
            user_language_settings[userid] = language_code
            await ctx.send(
                f"Default translation language set to '{SUPPORTED_LANGUAGES[language_code]}' for user <@{userid}>")
        else:
            await ctx.send(f"Invalid language. Please choose from supported languages or 'none'.")
add_help('General', 'translang <language code/off> [user]', 'Enables automatic translation and to a language for yourself or a user')


@bot.command(name='supported_languages', aliases=['langs', 'languages', 'translangs'])
async def show_supported_languages(ctx):
    languages_list = "\n".join([f"`{lang_code}` - {lang_name}" for lang_code, lang_name in SUPPORTED_LANGUAGES.items()])
    await ctx.send(f"Supported Languages:\n{languages_list}")
add_help('General', 'languages', 'lists all available languages for translation and their language code')


@is_owner()
@bot.command()
async def update(ctx):
    url = api + "/get_release"
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
add_help('Owner', 'update', 'Updates the bot to the latest version')


if '-dev-' in current_version:
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
    add_help('DEV', 'pullupdate', 'pulls the latest development version of the bot')


    if config['plugins']:
        @is_owner()
        @bot.command()
        async def getplugin(ctx: discord.ApplicationContext, plugin: str = ''):
            url = api + f"/get_plugin/{plugin}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(f'plugins/{plugin}.py', 'w', encoding='utf-8') as script_file:
                        script_file.write(response.text)
                    await ctx.send("Plugin downloaded, please restart bot")
                else:
                    await ctx.send(f"Failed to download plugin. Status code: {response.status_code}")
            except Exception as e:
                await ctx.send(f"Failed to download. Error: {e}")
        add_help('DEV', 'getplugin <plugin>', 'downloads a plugin from the official in progress plugins list')

if config['plugins']:

    @is_owner()
    @bot.command(name='downloadplugin')
    async def download_plugin_group(ctx, plugin_name:str = None):
        if plugin_name:
            url = api + f"/get_plugin_release/{current_version}/{plugin_name}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(f'plugins/{plugin_name}.py', 'w', encoding='utf-8') as script_file:
                        script_file.write(response.text)
                    await ctx.send("Plugin downloaded, please restart bot")
                else:
                    await ctx.send(f"Failed to download plugin. Status code: {response.status_code}")
            except Exception as e:
                await ctx.send(f"Failed to download. Error: {e}")
        else:
            plugin_list = requests.get(f'{api}/get_plugins_list/{current_version}').json()
            response = '# Available plugins:\n'
            for plugin in plugin_list:
                response += f"- **{plugin[:-3]}**\n"
            response += f'**To download a plugin use:** `{bot_prefix}downloadplugin [plugin name]`'
            await ctx.send(response)
        add_help('Owner', 'downloadplugin [plugin name]', 'downloads a plugin from the official plugins list or lists all the available plugins if no arguments provide')


    @is_owner()
    @bot.command()
    async def rmplugin(ctx: discord.ApplicationContext, plugin: str = ''):
        if not os.path.exists(f'plugins/{plugin}.py'):
            return await ctx.send('Plugin not found')
        try:
            os.remove(f'plugins/{plugin}.py')
            await ctx.send(f'Plugin: {plugin} removed successfully! Please restart the bot')
        except Exception as e:
            await ctx.send(f'An error occurred: {e}')
    add_help('Owner', 'rmplugin <plugin>', 'deletes an installed plugin')


    @is_owner()
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
    add_help('Owner', 'plugins', 'Lists the available plugins')


    @is_owner()
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
    add_help('Owner', 'pluginsall', 'shows all files in plugins folder')


    @is_owner()
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
    add_help('Owner', 'disableplugin <plugin>', 'disables a plugin')


    @is_owner()
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
    add_help('Owner', 'enableplugin <plugin>', 'Enables a plugin')


@bot.command(name='autoroleadd')
@has_required_perm()
async def autoroleadd(ctx, role: discord.Role):
    guild_id = str(ctx.guild.id)
    if guild_id not in server_roles:
        server_roles[guild_id] = []
    if role.id not in server_roles[guild_id]:
        server_roles[guild_id].append(role.id)
        save_roles()
        await ctx.send(f'Role {role.mention} added to auto-roles for this server.')
    else:
        await ctx.send(f'Role {role.mention} is already in the auto-roles list.')
add_help('Moderation', 'autoroleadd <role>', 'adds a role to auto role list')


@bot.command(name='autoroleremove')
@has_required_perm()
async def autoroleremove(ctx, role: discord.Role):
    guild_id = str(ctx.guild.id)
    if guild_id in server_roles and role.id in server_roles[guild_id]:
        server_roles[guild_id].remove(role.id)
        save_roles()
        await ctx.send(f'Role {role.mention} removed from auto-roles for this server.')
    else:
        await ctx.send(f'Role {role.mention} is not in the auto-roles list.')
add_help('Moderation', 'autoroleremove <role>', 'removes a role from the auto role list')


@bot.command(name='autoroles')
@has_required_perm()
async def autoroles(ctx):
    guild_id = str(ctx.guild.id)
    if guild_id in server_roles and server_roles[guild_id]:
        roles_list = []
        for role_id in server_roles[guild_id]:
            role_object: discord.Role = get(ctx.guild.roles, id=role_id)
            if role_object:
                roles_list.append(role_object.name)
            else:
                server_roles[guild_id].remove(role_id)
                roles_list.append(f"`Role ID {role_id} (deleted)`")

        roles_display = "\n".join(roles_list)
        await ctx.send(f"Auto-roles for this server:\n{roles_display}")
    else:
        await ctx.send("There are no auto-roles configured for this server.")
add_help('Moderation', 'autoroles', 'lists all the autoroles for the server ')


@bot.command('buttons')
@has_required_perm()
async def buttons_(ctx, *, arg: str):
    arg = arg.split(' ')
    if arg[0] == 'list':
        msg = '# Registered Buttons are:-\n'
        for item in button_configurations:
            button = item['custom_id']
            msg += f'{button}\n'
        await ctx.send(msg)
    elif arg[0] == 'send':
        if arg[1] in button_views:
            await ctx.send(view=button_views[arg[1]])
        else:
            await ctx.send('Given button not registered')
    elif arg[0] == 'combine' and arg[1] == 'send':
        buttons_to_combine = arg[2:]
        combined_view = View()
        for button_id in buttons_to_combine:
            if button_id in button_views:
                for child in button_views[button_id].children:
                    if isinstance(child, Button):
                        combined_view.add_item(child)
            else:
                await ctx.send(f'Button with id {button_id} not registered')
                return
        await ctx.send(view=combined_view)
    elif arg[0] == 'create':
        label = arg[1]
        if arg[2] == 'red':
            style = discord.ButtonStyle.red
        elif arg[2] == 'blue':
            style = discord.ButtonStyle.blurple
        elif arg[2] == 'green':
            style = discord.ButtonStyle.green
        elif arg[2] == 'gray':
            style = discord.ButtonStyle.gray
        custom_id = arg[3]
        callback = default_callback
        emoji = arg[4]
        view = create_button_view(label, style, custom_id, callback, emoji)
        await ctx.send(view=view)
    else:
        await ctx.send('Invalid command or arguments')


personal_vcs = {}
DATA_FILE = 'guild_vcs_data.json'


def load_vc_data():
    global guild_vcs
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            guild_vcs = json.load(f)
            return guild_vcs
    else:
        return {}


guild_vcs = load_vc_data()


def save_vc_data():
    with open(DATA_FILE, 'w') as f:
        json.dump(guild_vcs, f)


@bot.command(name="setupvc")
@has_required_perm()
async def setupvc(ctx, user_limit: int = 0):
    guild_id = str(ctx.guild.id)
    category = None

    join_to_create_channel = await ctx.guild.create_voice_channel('Join to Create VC', category=category)

    if guild_id not in guild_vcs:
        guild_vcs[guild_id] = {}

    guild_vcs[guild_id][str(join_to_create_channel.id)] = {"user_limit": user_limit}

    save_vc_data()

    await ctx.send(
        f"Join to Create VC created: {join_to_create_channel.mention}. Private VCs will have a user limit of {user_limit if user_limit > 0 else 'unlimited'}.")
add_help('Moderation', 'setupvc [limit]', 'join to create vc channel with optional limit')


@has_required_perm()
@bot.command('join')
async def join_vc(ctx: discord.ApplicationContext, vc: discord.VoiceChannel = None):
    if not vc:
        user = ctx.author
        if user.voice and user.voice.channel:
            await user.voice.channel.connect()
        else:
            await ctx.send('You are not connected to a voice channel!')
    else:
        try:
            await vc.connect()
        except Exception as e:
            await ctx.send(f'An error occurred: {e}')
add_help('Moderation', 'join', 'makes the bot join vc')


@has_required_perm()
@bot.command('discon')
async def disconnect_vc(ctx: discord.ApplicationContext, user: discord.Member = None):
    if not user:
        client = ctx.guild.voice_client
        if client:
            await client.disconnect()
    elif user.voice:
        channel = user.voice.channel.name
        await user.move_to(None)
        await ctx.send(f' disconnected {user.display_name} from {channel}')
    else:
        await ctx.send(f'{user.display_name} is not connected to a voice channel')
add_help('Moderation', 'discon [user]', 'disconnets the bot if it has joined the vc or a user')


@has_required_perm()
@bot.group()
async def embed(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f"Invalid embed command")

add_help('Moderation', 'embed <create/edit/addfield/deletefield/editfield/setcolor/setimage/setthumbnail/delete/send/list>', 'embed commands')

@has_required_perm()
@embed.command(name='create')
async def create_embed(ctx, name: str = None, *, content: str = None):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    if not name:
        return await ctx.send('Please provide a name')
    if name in embeds:
        await ctx.send(f"An embed with the name `{name}` already exists. Use `/embed edit` to modify it.")
        return

    if not content:
        content = f'This embed was created by {ctx.author.mention}'

    embed_dict = {
        "title": "",
        "description": content,
        "color": 0,
        "fields": [],
        "footer": "",
        "image": "",
        "thumbnail": ""
    }
    server_configs.setdefault(str(ctx.guild.id), {}).setdefault('embeds', {})[name] = embed_dict
    save_server_configs(server_configs)
    embed = get_embed(name, ctx.author)
    await ctx.send(f"Embed `{name}` has been created.", embed=embed)


@has_required_perm()
@embed.command(name='edit')
async def edit_embed(ctx, name: str = None, field: str = None, *, value: str = None):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    if not name or not field or not value:
        return await ctx.send("Please provide name field and value")

    if name not in embeds:
        await ctx.send(f"No embed found with the name `{name}`. Use `/embed create` to create it first.")
        return

    if field not in ["title", "description", "footer"]:
        await ctx.send("You can only edit `title`, `description`, or `footer` with this command.")
        return

    server_configs.setdefault(str(ctx.guild.id), {}).setdefault('embeds', {})[name][field] = value
    save_server_configs(server_configs)
    embed = get_embed(name, ctx.author)
    await ctx.send(f"Embed `{name}` has been updated: {field} set to `{value}`.", embed=embed)


@has_required_perm()
@embed.command(name='addfield')
async def add_field(ctx, name: str, title: str, value: str, inline: bool = False):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    if name not in embeds:
        await ctx.send(f"No embed found with the name `{name}`.")
        return

    server_configs.setdefault(str(ctx.guild.id), {}).setdefault('embeds', {})[name]["fields"].append({"name": title, "value": value, "inline": inline})
    save_server_configs(server_configs)
    embed = get_embed(name, ctx.author)
    await ctx.send(f"Field added to embed `{name}`.", embed=embed)


@has_required_perm()
@embed.command(name='delfield')
async def delete_field(ctx, name: str, index: int):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    if name not in embeds:
        await ctx.send(f"No embed found with the name `{name}`.")
        return

    try:
        server_configs.setdefault(str(ctx.guild.id), {}).setdefault('embeds', {})[name]["fields"].pop(index)
        save_server_configs(server_configs)
        embed = get_embed(name, ctx.author)
        await ctx.send(f"Field `{embeds['name']}` has been removed from embed `{name}`.", embed=embed)
    except IndexError:
        await ctx.send("Invalid field index. Please check the embed and try again.")


@has_required_perm()
@embed.command(name='editfield')
async def edit_field(ctx, name: str, index: int, title: str = None, value: str = None, inline: bool = None):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    if name not in embeds:
        await ctx.send(f"No embed found with the name `{name}`.")
        return

    try:
        field = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})[name]["fields"][index]
        if title is not None:
            field["name"] = title
        if value is not None:
            field["value"] = value
        if inline is not None:
            field["inline"] = inline

        save_server_configs(server_configs)
        embed = get_embed(name, ctx.author)
        await ctx.send(f"Field at index `{index}` in embed `{name}` has been updated.", embed=embed)
    except IndexError:
        await ctx.send("Invalid field index. Please check the embed and try again.")


@has_required_perm()
@embed.command(name='setcolor')
async def set_color_embed(ctx, name: str, color: str):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    if name not in embeds:
        await ctx.send(f"No embed found with the name `{name}`.")
        return

    try:
        if color.startswith("#"):
            color = color[1:]
        server_configs.setdefault(str(ctx.guild.id), {}).setdefault('embeds', {})[name]["color"] = int(color, 16)
        save_server_configs(server_configs)
        embed = get_embed(name, ctx.author)
        await ctx.send(f"Color updated for embed `{name}`.", embed=embed)
    except ValueError:
        await ctx.send("Invalid color code. Please provide a valid hexadecimal color (e.g., #3498db).")


@has_required_perm()
@embed.command(name='setimage')
async def set_image_embed(ctx, name: str, image: str = ""):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    if name not in embeds:
        await ctx.send(f"No embed found with the name `{name}`.")
        return

    try:
        if image in ['none', 'null']:
            image = ""
        server_configs.setdefault(str(ctx.guild.id), {}).setdefault('embeds', {})[name]["image"] = image
        save_server_configs(server_configs)
        embed = get_embed(name, ctx.author)
        await ctx.send(f"Image updated for embed `{name}`.", embed=embed)
    except ValueError:
        await ctx.send("Invalid color code. Please provide a valid hexadecimal color (e.g., #3498db).")


@has_required_perm()
@embed.command(name='setthumbnail')
async def set_thumbnail_embed(ctx, name: str, thumbnail: str = ""):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    if name not in embeds:
        await ctx.send(f"No embed found with the name `{name}`.")
        return

    try:
        if thumbnail in ['none', 'null']:
            thumbnail = ""
        server_configs.setdefault(str(ctx.guild.id), {}).setdefault('embeds', {})[name]["thumbnail"] = thumbnail
        save_server_configs(server_configs)
        embed = get_embed(name, ctx.author)
        await ctx.send(f"Thmbnail updated for embed `{name}`.", embed=embed)
    except ValueError:
        await ctx.send("Invalid color code. Please provide a valid hexadecimal color (e.g., #3498db).")


@has_required_perm()
@embed.command(name='delete')
async def delete_embed(ctx, name: str):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    if name not in embeds:
        await ctx.send(f"No embed found with the name `{name}`.")
        return

    del server_configs.setdefault(str(ctx.guild.id), {}).setdefault('embeds', {})[name]
    save_server_configs(server_configs)
    await ctx.send(f"Embed `{name}` has been deleted.")


@has_required_perm()
@embed.command(name='send')
async def send_embed(ctx, *,name: str):
    embed = get_embed(name, ctx.author)
    target_channel = ctx.channel
    await target_channel.send(embed=embed)


@has_required_perm()
@embed.command(name='list')
async def list_embeds(ctx):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    try:
        embed_list = ', '.join(embeds) if embeds else "No embeds available."

        await ctx.send(f"Here are the available embeds:\n{embed_list}")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


@has_required_perm()
@bot.command(name='setwelcomechannel')
async def def_welcome_channel(ctx, channel: discord.TextChannel = None):
    global server_configs
    server_id = str(ctx.guild.id)
    if server_id not in server_configs:
        server_configs[server_id] = {}
    server_configs[server_id]['welcome_channel_id'] = channel.id if channel else ctx.channel.id
    save_server_configs(server_configs)
    await ctx.channel.send('Welcome channel defined successfully')
add_help('Moderation', 'setwelcomechannel <channel>', 'defines the welcome message channel of a server')


@has_required_perm()
@bot.command(name='rmwelcomechannel')
async def rm_welcome_channel(ctx):
    server_id = str(ctx.guild.id)

    if server_id not in server_configs:
        server_configs[server_id] = {}

    if 'welcome_channel_id' not in server_configs[server_id]:
        await ctx.send('No welcome channel defined')
        return
    server_configs[server_id].pop('welcome_channel_id')
    save_server_configs(server_configs)
    await ctx.send('Welcome channel removed successfully')
add_help('Moderation', 'rmwelcomechannel', 'removes the defined welcome message channel')


@has_required_perm()
@bot.command(name='setwelcomeembed')
async def def_welcome_embed(ctx, *, name:str = None):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    server_id = str(ctx.guild.id)
    if not name in embeds:
        await ctx.send('No embed of that name exists')
        return
    if server_id not in server_configs:
        server_configs[server_id] = {}

    server_configs[str(ctx.guild.id)]['welcome_embed'] = name
    save_server_configs(server_configs)

    await ctx.channel.send('Welcome embed defined successfully')
add_help('Moderation', 'setwelcomeembed <embed name>', 'sets the welcome embed for the server')


@has_required_perm()
@bot.command(name='setleavechannel')
async def def_leave_channel(ctx, channel: discord.TextChannel = None):
    global server_configs
    server_id = str(ctx.guild.id)
    if server_id not in server_configs:
        server_configs[server_id] = {}
    server_configs[server_id]['leave_channel_id'] = channel.id if channel else ctx.channel.id
    save_server_configs(server_configs)
    await ctx.channel.send('Leave channel defined successfully')
add_help('Moderation', 'setleavechannel <channel>', 'defines the leave message channel of a server')


@has_required_perm()
@bot.command(name='rmleavechannel')
async def rm_leave_channel(ctx):
    server_id = str(ctx.guild.id)

    if server_id not in server_configs:
        server_configs[server_id] = {}

    if 'leave_channel_id' not in server_configs[server_id]:
        await ctx.send('No Leave channel defined')
        return
    server_configs[server_id].pop('leave_channel_id')
    save_server_configs(server_configs)
    await ctx.send('Leave channel removed successfully')
add_help('Moderation', 'rmleavechannel', 'removes the defined leave message channel')


@has_required_perm()
@bot.command(name='setleaveembed')
async def def_leave_embed(ctx, *, name:str = None):
    embeds = server_configs.get(str(ctx.guild.id), {}).get('embeds', {})
    server_id = str(ctx.guild.id)
    if not name in embeds:
        await ctx.send('No embed of that name exists')
        return
    if server_id not in server_configs:
        server_configs[server_id] = {}

    server_configs[str(ctx.guild.id)]['leave_embed'] = name
    save_server_configs(server_configs)

    await ctx.channel.send('Leave embed defined successfully')
add_help('Moderation', 'setleaveembed <embed name>', 'defines the leave embed for the server')


@has_required_perm()
@bot.command(name='setmembercountchannel')
async def def_member_count_channel(ctx, channel: discord.abc.GuildChannel = None):
    server_id = str(ctx.guild.id)
    if server_id not in server_configs:
        server_configs[server_id] = {}
    if not channel:
        channel = ctx.channel

    server_configs[str(ctx.guild.id)]['member_count_channel'] = int(channel.id) if channel else None
    save_server_configs(server_configs)

    await ctx.channel.send('Member Count Channel defined successfully')
add_help('Moderation', 'setmembercountchannel <channel>', 'removes the defined welcome message channel')


@bot.group()
async def antinuke(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send('Please use a valid subcommand: enable, disable, setlogschannel, rmlogschannel, whitelist, trustlist')
add_help('Moderation', 'antinuke <enable/disable/setlogschannel/rmlogschannel/whitelist/trustlist>', 'antinuke commands')


@antinuke.command(name='enable')
async def enable_antinuke(ctx):
    if not is_trusted(ctx.guild, ctx.author):
        return await ctx.send('You are not authorized to use this command!')
    if not server_configs.get(str(ctx.guild.id)):
        server_configs[str(ctx.guild.id)] = {}
    server_configs[str(ctx.guild.id)]['antinuke'] = True
    save_server_configs(server_configs)
    await ctx.send("Antinuke enabled for this server")


@antinuke.command(name='disable')
async def disable_antinuke(ctx):
    if not is_trusted(ctx.guild, ctx.author):
        return await ctx.send('You are not authorized to use this command!')
    if not server_configs.get(str(ctx.guild.id)):
        server_configs[str(ctx.guild.id)] = {}
    server_configs[str(ctx.guild.id)]['antinuke'] = False
    save_server_configs(server_configs)
    await ctx.send("Antinuke disabled for this server")


@antinuke.command(name='setlogschannel')
async def set_logs_channel_antinuke(ctx, channel: discord.TextChannel = None):
    if not is_trusted(ctx.guild, ctx.author):
        return await ctx.send('You are not authorized to use this command!')
    if not channel:
        channel = ctx.channel

    if not server_configs.get(str(ctx.guild.id)):
        server_configs[str(ctx.guild.id)] = {}
    server_configs[str(ctx.guild.id)]['antinuke_logs_channel'] = channel.id
    save_server_configs(server_configs)
    await ctx.send("Antinuke logs channel defined successfully")


@antinuke.command(name='rmlogschannel')
async def rm_logs_channel_antinuke(ctx):
    if not is_trusted(ctx.guild, ctx.author):
        return await ctx.send('You are not authorized to use this command!')
    if not server_configs.get(str(ctx.guild.id)):
        server_configs[str(ctx.guild.id)] = {}
    if server_configs[str(ctx.guild.id)].get('antinuke_logs_channel'):
        server_configs[str(ctx.guild.id)].pop('antinuke_logs_channel')
    save_server_configs(server_configs)
    await ctx.send("Antinuke logs channel removed successfully")


@antinuke.command(name='whitelist')
async def whitelist_antinuke(ctx, subcommand: str = None, user: discord.User = None):
    if not is_trusted(ctx.guild, ctx.author):
        return await ctx.send('You are not authorized to use this command!')
    guild_id = str(ctx.guild.id)
    if not server_configs.get(str(ctx.guild.id)):
        server_configs[str(ctx.guild.id)] = {}
    if not subcommand and not user:
        return await ctx.send("**Current whitelist:**\n" + "\n - ".join(f"- <@{user_id}>" for user_id in server_configs[guild_id]['antinuke_whitelist']))

    if not subcommand or not user:
        return await ctx.send("Please provide a subcommand add or remove and a user")
    if subcommand == 'add':
        if not server_configs[guild_id].get('antinuke_whitelist'):
            server_configs[guild_id]['antinuke_whitelist'] = []
        if not user.id in server_configs[guild_id]['antinuke_whitelist']:
            server_configs[guild_id]['antinuke_whitelist'].append(user.id)
        save_server_configs(server_configs)
        await ctx.send("User added to whitelist successfully")
    if subcommand == 'remove':
        if not server_configs[guild_id].get('antinuke_whitelist'):
            server_configs[guild_id]['antinuke_whitelist'] = []
        if user.id in server_configs[guild_id]['antinuke_whitelist']:
            server_configs[guild_id]['antinuke_whitelist'].remove(user.id)
        save_server_configs(server_configs)
        await ctx.send("User removed from whitelist successfully")


@antinuke.command(name='trust')
async def trust_antinuke(ctx, subcommand: str = None, user: discord.User = None):
    if not is_trusted(ctx.guild, ctx.author):
        return await ctx.send('You are not authorized to use this command!')
    guild_id = str(ctx.guild.id)
    if not server_configs.get(str(ctx.guild.id)):
        server_configs[str(ctx.guild.id)] = {}
    if not subcommand and not user:
        return await ctx.send("**Current trust list:**\n" + "\n - ".join(
            f"- <@{user_id}>" for user_id in server_configs[guild_id]['antinuke_trustlist']))
    if not subcommand or not user:
        return await ctx.send("Please provide a subcommand add or remove and a user")
    if subcommand == 'add':
        if not server_configs[guild_id].get('antinuke_trustlist'):
            server_configs[guild_id]['antinuke_trustlist'] = []
        if not user.id in server_configs[guild_id]['antinuke_trustlist']:
            server_configs[guild_id]['antinuke_trustlist'].append(user.id)
        save_server_configs(server_configs)
        await ctx.send("User added to trust list successfully")
    if subcommand == 'remove':
        if not server_configs[guild_id].get('antinuke_trustlist'):
            server_configs[guild_id]['antinuke_trustlist'] = []
        if user.id in server_configs[guild_id]['antinuke_trustlist']:
            server_configs[guild_id]['antinuke_trustlist'].remove(user.id)
        save_server_configs(server_configs)
        await ctx.send("User removed from trust list successfully")


@bot.command(name='authorization')
@has_owner_perm()
async def authorization_server(ctx, subcommand: str = None, user: discord.User = None):
    guild_id = str(ctx.guild.id)
    if not server_configs.get(str(ctx.guild.id)):
        server_configs[str(ctx.guild.id)] = {}
    if not subcommand and not user:
        return await ctx.send("**Current authorized list:**\n" + "\n - ".join(
            f"- <@{user_id}>" for user_id in server_configs[guild_id]['authorized_users']))
    if not subcommand or not user:
        return await ctx.send("Please provide a subcommand add or remove and a user")
    if subcommand == 'add':
        if not server_configs[guild_id].get('authorized_users'):
            server_configs[guild_id]['authorized_users'] = []
        if not user.id in server_configs[guild_id]['authorized_users']:
            server_configs[guild_id]['authorized_users'].append(user.id)
        save_server_configs(server_configs)
        await ctx.send("User added to authorized list successfully")
    if subcommand == 'remove':
        if not server_configs[guild_id].get('authorized_users'):
            server_configs[guild_id]['authorized_users'] = []
        if user.id in server_configs[guild_id]['authorized_users']:
            server_configs[guild_id]['authorized_users'].remove(user.id)
        save_server_configs(server_configs)
        await ctx.send("User removed from authorized list successfully")
add_help('Moderation', 'authorization <add/remove> <user>', 'Authorizes users for Moderation level command permissions')


@bot.command(name='owner')
@has_owner_perm()
async def ownerization_server(ctx, subcommand: str = None, user: discord.User = None):
    guild_id = str(ctx.guild.id)
    if not server_configs.get(str(ctx.guild.id)):
        server_configs[str(ctx.guild.id)] = {}
    if not subcommand and not user:
        return await ctx.send("**Current owner list:**\n" + "\n - ".join(
            f"- <@{user_id}>" for user_id in server_configs[guild_id]['owners']))
    if not subcommand or not user:
        return await ctx.send("Please provide a subcommand add or remove and a user")
    if subcommand == 'add':
        if not server_configs[guild_id].get('owners'):
            server_configs[guild_id]['owners'] = []
        if not user.id in server_configs[guild_id]['owners']:
            server_configs[guild_id]['owners'].append(user.id)
        save_server_configs(server_configs)
        await ctx.send("User added to authorized list successfully")
    if subcommand == 'remove':
        if not server_configs[guild_id].get('owners'):
            server_configs[guild_id]['owners'] = []
        if user.id in server_configs[guild_id]['owners']:
            server_configs[guild_id]['owners'].remove(user.id)
        save_server_configs(server_configs)
        await ctx.send("User removed from authorized list successfully")
add_help('Moderation', 'owner <add/remove> <user>', 'Authorizes users for Server owner level command permissions')


timers_file = "timers.json"

def load_timers():
    try:
        with open(timers_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_timers(timers):
    with open(timers_file, "w") as f:
        f.write(json.dumps(timers))

def parse_duration(duration_str):
    pattern = r"(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?"
    match = re.fullmatch(pattern, duration_str)
    if not match:
        return None

    weeks, days, hours, minutes, seconds = [int(value) if value else 0 for value in match.groups()]
    return timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)


@bot.group(name='timer', invoke_without_command=True)
async def timers_group(ctx):
    embed = discord.Embed(title="Timer Commands",
                          description=f"Use `{bot_prefix}timer add`, `{bot_prefix}timer list`, or `{bot_prefix}timer delete`.",
                          color=discord.Color.blurple())
    await ctx.send(embed=embed)
add_help('General', 'timer <set/list/delete> [1h/m/s/d/w]', 'sets a timer and notifes you when the timer ends')


@timers_group.command(name="add", aliases=['set'])
async def timer_add(ctx, duration: str):
    timers = load_timers()
    try:
        channel_id = str(ctx.channel.id)
        user_id = str(ctx.author.id)
        delta = parse_duration(duration)
        if delta is None:
            await ctx.send(embed=discord.Embed(
                description="❌ Invalid duration format! Use `1h2m3s`, `10s`, etc.",
                color=discord.Color.red()))
            return

        end_time = datetime.now(timezone.utc) + delta

        if user_id not in timers:
            timers[user_id] = {}

        timers[user_id][end_time.isoformat()] = channel_id

        save_timers(timers)
        embed = discord.Embed(
            description=f"✅ Timer set for `{duration}`! \nwill end <t:{int(end_time.timestamp())}:R>",
            color=discord.Color.green())
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=discord.Embed(
            description=f"❌ An error occurred: {e}",
            color=discord.Color.red()))


@timers_group.command(name="list")
async def timer_list(ctx):
    timers = load_timers()
    user_id = str(ctx.author.id)
    if user_id not in timers or not timers[user_id]:
        await ctx.send(embed=discord.Embed(
            description="You have no active timers.",
            color=discord.Color.blurple()))
        return

    embed = discord.Embed(title="Your Active Timers",
                          color=discord.Color.blurple())
    for end_time, channel_id in timers[user_id].items():
        remaining = datetime.fromisoformat(end_time) - datetime.now(timezone.utc)
        if remaining.total_seconds() > 0:
            embed.add_field(
                name=f"Ends in {str(remaining).split('.')[0]}",
                value=f"Channel: <#{channel_id}>",
                inline=False
            )

    await ctx.send(embed=embed)


@timers_group.command(name="delete", aliases=['remove'])
async def timer_delete(ctx, timer_id: int = None):
    timers = load_timers()
    user_id = str(ctx.author.id)

    if user_id not in timers or not timers[user_id]:
        await ctx.send(embed=discord.Embed(
            description="❌ You have no active timers.",
            color=discord.Color.red()))
        return

    user_timers = list(timers[user_id].items())

    if timer_id is None:
        embed = discord.Embed(
            title="⏳ Your Active Timers",
            description="\n".join(
                [f"`{i + 1}`: Ends at `{end_time}`" for i, (end_time, _) in enumerate(user_timers)]
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Use {bot_prefix}delete <ID> to delete a specific timer.")
        await ctx.send(embed=embed)
        return

    if timer_id < 1 or timer_id > len(user_timers):
        await ctx.send(embed=discord.Embed(
            description="❌ Invalid timer ID.",
            color=discord.Color.red()))
        return

    end_time, _ = user_timers[timer_id - 1]
    del timers[user_id][end_time]
    if not timers[user_id]:
        del timers[user_id]

    save_timers(timers)
    await ctx.send(embed=discord.Embed(
        description=f"✅ Timer ending at `{end_time}` deleted!",
        color=discord.Color.green()))


@tasks.loop(seconds=1)
async def check_timers():
    timers = load_timers()
    now = datetime.now(timezone.utc)
    expired = []

    for user_id, user_timers in timers.items():
        for end_time, channel_id in list(user_timers.items()):
            try:
                end_time_obj = datetime.fromisoformat(end_time)
                if end_time_obj <= now:
                    expired.append((user_id, end_time, channel_id))
            except ValueError as e:
                print(f"Skipping invalid timer: {end_time}. Error: {e}")

    for user_id, end_time, channel_id in expired:
        channel = bot.get_channel(int(channel_id))
        if channel:
            embed = discord.Embed(
                title="⏰ Timer Expired",
                description=f"<@{user_id}>, your timer has ended!",
                color=discord.Color.orange())
            await channel.send(f'<@{user_id}>',embed=embed)
        del timers[user_id][end_time]
        if not timers[user_id]:
            del timers[user_id]

    if expired:
        save_timers(timers)


@bot.group(invoke_without_command = True)
async def bannedwords(ctx):
    if ctx.invoked_subcommand is None:
        embed = discord.Embed(
            title="Invalid Command",
            description="Please use a valid subcommand for bannedwords: add, remove, list, action.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)


@bannedwords.command(name="add")
async def banned_words_add(ctx, *, word):
    if not word:
        embed = discord.Embed(
            title="Error",
            description="You need to specify a word to add to the banned words list.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    if word in server_configs.get(guild_id, {}).get("bannable_words", []):
        embed = discord.Embed(
            title="Word Already Exists",
            description=f'"{word}" is already in the banned words list.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    server_configs.setdefault(guild_id, {}).setdefault("bannable_words", []).append(word)
    save_server_configs(server_configs)
    embed = discord.Embed(
        title="Word Added",
        description=f'"{word}" has been added to the banned words list.',
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
add_help('Moderation','`bannedwords add <word/*word/word*/*word*/regex>`', 'addes a word to the banned words list, if a banned word is said anywhere on the server it would take action')


@bannedwords.command(name="remove")
async def banned_words_remove(ctx, *, word):
    if not word:
        embed = discord.Embed(
            title="Error",
            description="You need to specify a word to remove from the banned words list.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    guild_id = str(ctx.guild.id)
    if word not in server_configs.get(guild_id, {}).get("bannable_words", []):
        embed = discord.Embed(
            title="Word Not Found",
            description=f'"{word}" is not in the banned words list.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    server_configs[guild_id]["bannable_words"].remove(word)
    save_server_configs(server_configs)
    embed = discord.Embed(
        title="Word Removed",
        description=f'"{word}" has been removed from the banned words list.',
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
add_help('Moderation', 'bannedwords remove <word>', 'removes a word from the banned words list')


@bannedwords.command(name="list")
async def banned_words_list(ctx):
    guild_id = str(ctx.guild.id)
    words = server_configs.get(guild_id, {}).get("bannable_words", [])
    embed = discord.Embed(
        title="Banned Words List",
        description="No banned words set." if not words else "\n- ".join(words),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)
add_help("Moderation", "bannedwords list", 'Lists all the banned words added')


@bannedwords.command(name="action")
async def banned_words_action(ctx, threshold: int, action: str, duration: str, *, message: str = None):
    if action not in ["warn", "mute", "ban"]:
        embed = discord.Embed(
            title="❌ Invalid Action",
            description="Valid actions: `warn`, `mute`, `ban`.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    parsed_duration = parse_duration(duration)
    if not parsed_duration:
        embed = discord.Embed(
            title="❌ Invalid Duration",
            description="Use format: `1w2d3h4m5s` (weeks, days, hours, minutes, seconds).",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return

    duration_seconds = int(parsed_duration.total_seconds())

    guild_id = str(ctx.guild.id)
    server_configs.setdefault(guild_id, {}).setdefault("action_settings", {})[str(threshold)] = {
        "action": action,
        "timeframe": duration_seconds
    }
    save_server_configs(server_configs)

    if message:
        server_configs[guild_id]["action_settings"][str(threshold)]["message"] = message

    embed = discord.Embed(
        title="✅ Action Set",
        description=f"**Threshold:** {threshold} violations\n"
                    f"**Action:** {action.capitalize()}\n"
                    f"**Timeframe:** {duration} ({duration_seconds} seconds)\n"
                    f"**Custom Message:** {message if message else 'None'}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)
add_help('Moderation', 'bannedwords action <threshold> <mute/ban/warn> <timeframe> [message]', 'Actions to take when given amount of banned words are said in given amount of time')


@has_required_perm()
@bot.group(name='chatcooldown', invoke_without_command=True)
async def chatcooldown(ctx):
    await ctx.send('Please use a valid subcommand: add, remove, window <message window in seconds>, cooldownmax <in seconds>, cooldownmin <in seconds>, threshold <amount>, minimumtheshold')
add_help('Moderation', 'chatcooldown', 'automatically change cooldown depending on chat activity')


@has_required_perm()
@chatcooldown.command(name='add')
async def chatcooldown_add(ctx):
    guild_id = str(ctx.guild.id)
    server_configs.setdefault(guild_id, {}).setdefault('cooldown_channels', []).append(ctx.channel.id)
    save_server_configs(server_configs)
    await ctx.send('Channel added successfully')
add_help('Moderation', 'chatcooldown add', 'adds the current channel to the active list')


@has_required_perm()
@chatcooldown.command(name='remove')
async def chatcooldown_remove(ctx):
    guild_id = str(ctx.guild.id)
    server_configs.setdefault(guild_id, {}).setdefault('cooldown_channels', [])

    if ctx.channel.id in server_configs[guild_id]['cooldown_channels']:
        server_configs[guild_id]['cooldown_channels'].remove(ctx.channel.id)
        save_server_configs(server_configs)
        await ctx.send("Cooldown removed from this channel.")
    else:
        await ctx.send("This channel is not in the cooldown list.")
add_help('Moderation', 'chatcooldown remove', 'removes the current channel from the active list')


@has_required_perm()
@chatcooldown.command(name='window')
async def chatcooldown_window(ctx, window: int=10):
    guild_id = str(ctx.guild.id)
    server_configs.setdefault(guild_id, {}).setdefault('cooldown_message_window', window)
    save_server_configs(server_configs)
    await ctx.send(f'Message window set to {window} seconds')
add_help('Moderation', 'chatcooldown window <amount in seconds>', 'sets the message window duration in seconds')


@has_required_perm()
@chatcooldown.command(name='threshold')
async def chatcooldown_threshold(ctx, threshold: int=10):
    guild_id = str(ctx.guild.id)
    server_configs.setdefault(guild_id, {}).setdefault('cooldown_message_threshold', threshold)
    save_server_configs(server_configs)
    await ctx.send(f'Message threshold set to {threshold} messages within message windiw to trigger max cooldown')
add_help('Moderation', 'chatcooldown threshold <amount>', 'sets the message threshold to trigger max cooldown')


@has_required_perm()
@chatcooldown.command(name='minimumthreshold')
async def chatcooldown_minimumthreshold(ctx, threshold: int=10):
    guild_id = str(ctx.guild.id)
    server_configs.setdefault(guild_id, {}).setdefault('cooldown_minimum_threshold', threshold)
    save_server_configs(server_configs)
    await ctx.send(f'Minimum threshold set to {threshold} messages within message window to trigger max cooldown')
add_help('Moderation', 'chatcooldown minimumthreshold <amount>', 'sets the minimum message threshold to trigger cooldown adjustments')


@has_required_perm()
@chatcooldown.command(name='cooldownmax')
async def chatcooldown_cooldownmax(ctx, cooldown: int=5):
    guild_id = str(ctx.guild.id)
    server_configs.setdefault(guild_id, {}).setdefault('cooldown_max', cooldown)
    save_server_configs(server_configs)
    await ctx.send(f'Max cooldown set to {cooldown} seconds')
add_help('Moderation', 'chatcooldown cooldownmax <seconds>', 'sets the maximum cooldown duration in seconds')


@has_required_perm()
@chatcooldown.command(name='cooldownmin')
async def chatcooldown_cooldownmin(ctx, cooldown: int=0):
    guild_id = str(ctx.guild.id)
    server_configs.setdefault(guild_id, {}).setdefault('cooldown_min', cooldown)
    save_server_configs(server_configs)
    await ctx.send(f'Minimum cooldown set to {cooldown} seconds')
add_help('Moderation', 'chatcooldown cooldownmin <seconds>', 'sets the minimum cooldown duration in seconds')


@has_required_perm()
@bot.group('levelrewards', invoke_without_command=True)
async def levelrewards(ctx):
    await ctx.send('Please use valid subcommand enable/disable, add <message amount> <role>, remove <message count>, exclude')
add_help('Moderation', 'levelrewards', 'command to setup levelrewards in the server')


@has_required_perm()
@levelrewards.command(name='enable')
async def level_rewards_enable(ctx):
    server_configs.setdefault(str(ctx.guild.id), {})['level_rewards'] = True
    save_server_configs(server_configs)
    await ctx.send('Level rewards enabled')


@has_required_perm()
@levelrewards.command(name='disable')
async def level_rewards_disable(ctx):
    server_configs.setdefault(str(ctx.guild.id), {})['level_rewards'] = False
    save_server_configs(server_configs)
    await ctx.send('Level rewards disabled')


@has_required_perm()
@levelrewards.command(name='add')
async def level_rewards_add(ctx, message_count: str = 10, role: discord.Role = None):
    server_configs.setdefault(str(ctx.guild.id), {}).setdefault('level_reward_roles', {})[message_count] = role.id
    save_server_configs(server_configs)
    await ctx.send(f'Level reward added! Members will receive the {role.mention} role at **{message_count}** messages.')


@has_required_perm()
@levelrewards.command(name='exclude')
async def level_rewards_exclude(ctx):
    if ctx.channel.id in server_configs.get(str(ctx.guild.id), {}).get('level_reward_excluded', []):
        server_configs.setdefault(str(ctx.guild.id), {}).setdefault('level_reward_excluded', []).remove(ctx.channel.id)
        return await ctx.send(f'{ctx.channel.mention} has been re-included in level rewards')
    server_configs.setdefault(str(ctx.guild.id), {}).setdefault('level_reward_excluded', []).append(ctx.channel.id)
    save_server_configs(server_configs)
    await ctx.send(f'{ctx.channel.mention} has been excluded from level rewards')


@bot.command(name='levels')
async def levels(ctx):
    guild_id = str(ctx.guild.id)
    level_rewards = server_configs.get(guild_id, {}).get('level_reward_roles', {})
    if not level_rewards:
        return await ctx.send("No level rewards configured for this server.")
    embed = discord.Embed(title="Level Rewards", color=discord.Color.blue())
    for message_count, role_id in sorted(level_rewards.items(), key=lambda x: int(x[0])):
        role = ctx.guild.get_role(role_id)
        if role:
            embed.add_field(name=f"{message_count} Messages", value=role.mention, inline=False)
    await ctx.send(embed=embed)
add_help('General', 'levels', 'lists all the available levels in the server')


@bot.command(name='level')
async def level(ctx, user: discord.Member = None):
    guild_id = str(ctx.guild.id)
    user = user if user else ctx.author
    user_id = str(user.id)
    if server_configs.get(guild_id, {}).get('level_rewards', False):
        user_messages = server_configs.get(guild_id, {}).get('user_messages', {}).get(user_id, 0)
        embed = discord.Embed(title=f"{user.display_name}'s Level", color=discord.Color.green())
        embed.add_field(name="Total Messages", value=str(user_messages), inline=False)
        level_rewards = server_configs.get(guild_id, {}).get('level_reward_roles', {})
        if level_rewards:
            current_level = max((int(level) for level in level_rewards if int(level) <= user_messages), default=0)
            next_level = min((int(level) for level in level_rewards if int(level) > user_messages), default=None)
            if current_level:
                current_role = ctx.guild.get_role(level_rewards[str(current_level)])
                if current_role:
                    embed.add_field(name="Current Level",
                                    value=f"{current_role.mention} (Reached at {current_level} messages)", inline=False)
            if next_level:
                next_role = ctx.guild.get_role(level_rewards[str(next_level)])
                if next_role:
                    embed.add_field(name="Next Reward", value=f"{next_role.mention} at {next_level} messages!",
                                    inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send('Level rewards are not enabled in this server.')
add_help('General', 'level', 'know your current level, if level rewards are setup in the server')


@has_required_perm()
@bot.command(name='reactionroles')
async def setup_reactionrole(ctx, emoji: str = None, role: discord.Role = None, message_reference: str = None):
    reaction_roles = server_configs.get(str(ctx.guild.id), {}).get('reaction_roles', {})
    try:
        if ctx.message.reference:
            message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        else:
            match = re.search(r'/(\d+)/(\d+)/(\d+)', message_reference)
            if not match:
                await ctx.send("Invalid message reference. Please reply to a message or provide a valid link.")
                return
            guild_id, channel_id, message_id = map(int, match.groups())
            channel = bot.get_channel(channel_id)
            if not channel:
                await ctx.send("Couldn't find the channel. Make sure the bot has access.")
                return
            message = await channel.fetch_message(message_id)
        if not emoji or not role:
            await ctx.send("Usage: Reply to a message OR use a link, then specify an emoji and a role mention.")
            return
        if str(message.id) not in reaction_roles:
            reaction_roles[str(message.id)] = {}
        server_configs.setdefault(str(ctx.guild.id), {}).setdefault('reaction_roles', {}).setdefault(str(message.id), {})[emoji] = role.id
        save_server_configs(server_configs)
        await message.add_reaction(emoji)
        await ctx.send(f"Reaction role set: {emoji} → {role.name} on message {message.jump_url}")
    except Exception as e:
        await ctx.send(f"Error: {e}")
add_help('Moderation', 'reactionrole <emoji> <role mention> <message link or message reply>', 'sets up a reaction role')


bot.remove_command('help')


@bot.command(name='help', aliases=['h'])
async def help(ctx, *, category: str = None):
    def create_pages(commands, category_name=None):
        pages = []
        current_page = f"# {category_name}\n\n" if category_name else ""
        for cmd, desc in commands.items():
            command_text = f"- **{bot_prefix}{cmd}**: {desc}\n"
            if len(current_page) + len(command_text) > 2000:
                pages.append(current_page)
                current_page = f"# {category_name}\n\n" if category_name else ""
                current_page += command_text
            else:
                current_page += command_text
        if current_page:
            pages.append(current_page)
        return pages

    if category:
        lower_category = category.lower()
        lower_helps = {key.lower(): value for key, value in helps.items()}
    if not category:
        help_msg = f"""
# Help Menu

**Basics:**
- <> - means mandatory arguments.
- [] - means optional arguments.

Use `{bot_prefix}help <category>` to browse commands.

**Current available categories are:**
- {'\n- '.join(helps.keys())}
        """
        pages = [help_msg]

    elif lower_category in lower_helps:
        commands = lower_helps[lower_category]
        pages = create_pages(commands, category)
    else:
        help_msg = f"Category '{category}' not found. Use `{bot_prefix}help` to see all available categories."
        pages = [help_msg]
    current_page = 0
    message = await ctx.send(pages[current_page])
    if len(pages) > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            await message.remove_reaction(reaction.emoji, user)

            if str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
                await message.edit(content=pages[current_page])
            elif str(reaction.emoji) == "➡️" and current_page < len(pages) - 1:
                current_page += 1
                await message.edit(content=pages[current_page])
        except asyncio.TimeoutError:
            await message.clear_reactions()
            break

async def default_callback(interaction):
    await interaction.respond(f'Pressed Button: {interaction.data["custom_id"]}')


def check_for_updates():
    try:
        state = "Latest"
        devbuild = False
        latest_release = str(requests.get(f'{api}/get_latest').json()["latest_version"]).strip('V')
        current_version_number = current_version.strip('V')

        if '-dev-' in current_version_number:
            current_version_number = current_version_number.split('-')[0]
            devbuild = True

        if float(latest_release) > float(current_version_number):
            outdated =   True
            state = "Outdated"
            logw(f'New version {latest_release} available!')
        else:
            outdated = False
        if devbuild:
            state = state + " Development Build"

        message = f"Running Current Version: {current_version} {state}"
        if outdated:
            message = message + f'\nNew version {latest_release} available!'
        return message
    except Exception as e:
        logw(f'Failed to check for updates due to an unexpected error: {e}')
        return f'Failed to check for updates due to an unexpected error: {e}'


if config['check_for_updates']:
    log(check_for_updates())


def log_to_file(message, date_string, log_dir):
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, 'log.txt')
    with open(log_file_path, 'a', encoding='utf-8') as file:
        file.write(message + '\n')


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '', filename)


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


async def process_responses(message, responses):
    for key, response_data in responses.items():
        keywords = response_data['keywords']
        response = replace_placeholders(response_data['response'], message.author)
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
async def on_raw_reaction_add(payload):
    reaction_roles = server_configs.get(str(payload.guild_id), {}).get('reaction_roles', {})
    if str(payload.message_id) in reaction_roles:
        guild = bot.get_guild(payload.guild_id)
        role_id = reaction_roles[str(payload.message_id)].get(str(payload.emoji))
        if role_id:
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.add_roles(role)


@bot.event
async def on_raw_reaction_remove(payload):
    reaction_roles = server_configs.get(str(payload.guild_id), {}).get('reaction_roles', {})
    if str(payload.message_id) in reaction_roles:
        guild = bot.get_guild(payload.guild_id)
        role_id = reaction_roles[str(payload.message_id)].get(str(payload.emoji))
        if role_id:
            role = guild.get_role(role_id)
            member = guild.get_member(payload.user_id)
            if role and member:
                await member.remove_roles(role)


@bot.event
async def on_voice_state_update(member: discord.Member, before, after):
    global guild_vcs, personal_vcs
    guild_id = str(member.guild.id)

    if guild_id in guild_vcs:
        if after.channel and str(after.channel.id) in guild_vcs[guild_id]:
            join_to_create_id = str(after.channel.id)

            if member.id in personal_vcs and personal_vcs[member.id].guild.id == int(guild_id):
                await member.move_to(personal_vcs[member.id])
                return

            user_limit = guild_vcs[guild_id][join_to_create_id]["user_limit"]

            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(view_channel=True, connect=True),
                member: discord.PermissionOverwrite(view_channel=True, connect=True)
            }

            category = after.channel.category
            vc = await member.guild.create_voice_channel(f"{member.display_name}'s Room", overwrites=overwrites,
                                                         category=category,
                                                         user_limit=user_limit if user_limit > 0 else None)

            await member.move_to(vc)

            personal_vcs[member.id] = vc

        if before.channel and before.channel.id in [vc.id for vc in personal_vcs.values()]:
            if len(before.channel.members) == 0:
                owner_id = [user_id for user_id, vc in personal_vcs.items() if vc.id == before.channel.id]
                if owner_id:
                    await before.channel.delete()
                    del personal_vcs[owner_id[0]]

        for join_to_create_id in list(guild_vcs[guild_id].keys()):
            if not bot.get_channel(int(join_to_create_id)):
                del guild_vcs[guild_id][join_to_create_id]
                save_vc_data()

    if config['log']:
        date_string = ttime().strftime('%Y-%m-%d')
        time_string = ttime().strftime('%H-%M-%S')
        log_dir = os.path.join('Logs', date_string, sanitize_filename(member.guild.name), 'Voice States')

        if before.channel != after.channel:
            if before.channel is None:
                log_message = f'{member.guild.name} > {time_string} > {member.name} joined {after.channel.name}'
            elif after.channel is None:
                log_message = f'{member.guild.name} > {time_string} > {member.name} left {before.channel.name}'
            else:
                log_message = f'{member.guild.name} > {time_string} > {member.name} moved from {before.channel.name} to {after.channel.name}'
            log_to_file(log_message, date_string, log_dir)


@bot.event
async def on_member_update(before, after):
    if config['log']:
        date_string = ttime().strftime('%Y-%m-%d')
        time_string = ttime().strftime('%H-%M-%S')
        log_dir = os.path.join('Logs', date_string, sanitize_filename(after.guild.name), 'Member Updates')

        if before.roles != after.roles:
            removed_roles = [role for role in before.roles if role not in after.roles]
            added_roles = [role for role in after.roles if role not in before.roles]

            log_message = f'{after.guild.name} > {time_string} > {after.name} roles updated. '

            if removed_roles:
                log_message += f"Removed roles: {', '.join([role.name for role in removed_roles])}. "

            if added_roles:
                log_message += f"Added roles: {', '.join([role.name for role in added_roles])}. "

            if not (added_roles or removed_roles):
                log_message += "No changes in roles."

            log_to_file(log_message, date_string, log_dir)

        if before.name != after.name:
            log_message = f'{after.guild.name} > {time_string} > Username updated. Before: {before.name}, After: {after.name}'
            log_to_file(log_message, date_string, log_dir)


user_violations = defaultdict(list)


def contains_banned_word(message, guild_id):
    bannable_words = server_configs.get(str(guild_id), {}).get("bannable_words", [])
    words = message.split()

    for pattern in bannable_words:
        if pattern.startswith("*") and pattern.endswith("*"):
            regex = re.compile(re.escape(pattern.strip("*")), re.IGNORECASE)
        elif pattern.startswith("*"):
            regex = re.compile(re.escape(pattern.strip("*")) + r"$", re.IGNORECASE)
        elif pattern.endswith("*"):
            regex = re.compile(r"^" + re.escape(pattern.strip("*")), re.IGNORECASE)
        else:
            regex = re.compile(rf"\b{re.escape(pattern)}\b", re.IGNORECASE)
        if any(regex.search(word) for word in words):
            return True

    return False


async def take_action(user, guild, violations, current_time):
    guild_id = str(guild.id)

    for action_key, action_config in server_configs.get(guild_id, {}).get("action_settings", {}).items():
        threshold = int(action_key)
        timeframe = action_config.get("timeframe", 60)

        valid_violations = [t for t in user_violations[user.id] if t > current_time - timeframe]
        if len(valid_violations) >= threshold:
            action = action_config["action"]
            if action == "warn":
                msg = replace_placeholders(action_config.get("message", "You have been warned for using banned words."), user)
                try:
                    await user.send(msg)
                except:
                    pass
            elif action == "mute":
                mute_role = discord.utils.get(guild.roles, name="Muted")
                if mute_role:
                    await user.add_roles(mute_role)
            elif action == "ban":
                await guild.ban(user, reason="Repeated use of banned words.")
            break


when_message_functions = []
def when_message(function):
    when_message_functions.append(function)
    return function


message_log={}

@when_message
async def func_chat_cooldown(message):
    if isinstance(message.channel, discord.DMChannel):
        return
    guild_id = str(message.channel.guild.id)
    TRACKED_CHANNELS = server_configs.get(guild_id, {}).get('cooldown_channels', [])
    MESSAGE_WINDOW = server_configs.get(guild_id, {}).get('cooldown_message_window', 10 )
    MESSAGE_THRESHOLD = server_configs.get(guild_id, {}).get('cooldown_message_threshold', 10)
    MINIMUM_THRESHOLD = server_configs.get(guild_id, {}).get('cooldown_minimum_threshold', 2)
    MAX_SLOWMODE = server_configs.get(guild_id, {}).get('cooldown_max', 5)
    MIN_SLOWMODE = server_configs.get(guild_id, {}).get('cooldown_min', 0)

    if message.author.bot or message.channel.id not in TRACKED_CHANNELS:
        return

    channel = message.channel
    now = ttime()

    if channel.id not in message_log:
        message_log[channel.id] = deque()

    log = message_log[channel.id]
    log.append(now)

    while log and (now - log[0]).total_seconds() > MESSAGE_WINDOW:
        log.popleft()

    message_count = len(log)
    if message_count >= MESSAGE_THRESHOLD:
        cooldown = min(MAX_SLOWMODE, message_count // 2)
    elif message_count < MINIMUM_THRESHOLD:
        return
    else:
        cooldown = MIN_SLOWMODE

    return await channel.edit(slowmode_delay=cooldown)


@when_message
async def level_rewards_engine(message):
    if message.author.bot:
        return

    guild_id = str(message.guild.id)
    user_id = str(message.author.id)

    if not server_configs.get(guild_id, {}).get('level_rewards', False):
        return
    if message.channel.id in server_configs.get(guild_id, {}).get('level_reward_excluded', []):
        return
    server_configs.setdefault(guild_id, {}).setdefault('user_messages', {})
    server_configs[guild_id]['user_messages'][user_id] = server_configs[guild_id]['user_messages'].get(user_id, 0) + 1
    save_server_configs(server_configs)

    message_count = server_configs[guild_id]['user_messages'][user_id]
    level_rewards = {int(k): v for k, v in server_configs.get(guild_id, {}).get('level_reward_roles', {}).items()}

    if message_count in level_rewards:
        role = message.guild.get_role(level_rewards[message_count])
        if role:
            await message.author.add_roles(role)
            return await message.channel.send(f'Congrats {message.author.mention}, you have been given the {role.name} role!')
    return

@bot.event
async def on_message(message: discord.Message):
    await bot.process_commands(message)
    for f in when_message_functions:
        if inspect.iscoroutinefunction(f):
            await f(message)
        else:
            f(message)

    guild_id = str(message.guild.id if message.guild else None)
    violation_timeframe = server_configs.get(guild_id, {}).get("violation_timeframe", 60)

    if contains_banned_word(message.content, guild_id):
        ctx = await bot.get_context(message)
        if ctx.valid:
            return

        await message.delete()
        embed = discord.Embed(
            title="Banned Word Detected",
            description=f"{message.author.mention}, your message contained a banned word!",
            color=discord.Color.red()
        )
        await message.channel.send(embed=embed)

        current_time = message.created_at.timestamp()
        user_violations[message.author.id].append(current_time)

        user_violations[message.author.id] = [t for t in user_violations[message.author.id] if
                                              t > current_time - violation_timeframe]

        await take_action(message.author, message.guild, len(user_violations[message.author.id]), current_time)

    if not message.content.startswith(config['prefix']):
        if message.author.id in user_language_settings:
            target_lang = user_language_settings[message.author.id]
            if target_lang != 'none':
                try:
                    translated = await translator.translate(message.content, dest=target_lang)
                    await message.reply(f"[Translated to {SUPPORTED_LANGUAGES[target_lang]}]: {translated.text}")
                except Exception as e:
                    await message.channel.send(f"Translation failed: {str(e)}")

    user_id_str = str(message.author.id)

    if user_id_str in afk_users:
        afk_data = afk_users.pop(user_id_str)
        with open(afk_file, 'w') as f:
            json.dump(afk_users, f, indent=4)

        afk_start_time = datetime.fromisoformat(afk_data['time'])
        afk_duration = ttime() - afk_start_time

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
        if message.author.id != bot.user.id:
            for mention in message.mentions:
                if str(mention.id) in afk_users:
                    afk_message = afk_users[str(mention.id)]["message"]
                    afk_users[str(mention.id)]["mentions"].append({
                        "author": str(message.author),
                        "channel": f'[{str(message.channel)}]({message.jump_url})'
                    })
                    with open(afk_file, 'w') as f:
                        json.dump(afk_users, f, indent=4)
                    await message.channel.send(f"{mention.name} is AFK: {afk_message}")

    await process_responses(message, responses)

    if config['log']:
        date_string = ttime().strftime('%Y-%m-%d')
        time_string = ttime().strftime('%H-%M-%S')

        if message.content is None:
            msg = ''
        else:
            msg = message.content

        if isinstance(message.channel, discord.DMChannel):
            author_name = sanitize_filename(message.author.name)
            log_dir = os.path.join('Logs', date_string, 'DMs', author_name)
            log_message = f"[DM] {message.author} > {time_string}: {msg}"
        else:
            server_name = sanitize_filename(message.guild.name)
            channel_name = sanitize_filename(message.channel.name)
            log_dir = os.path.join('Logs', date_string, server_name, channel_name)
            log_message = f'{server_name} > #{channel_name} > {time_string} > {message.author.name}: {msg}'

        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, 'log.txt')

        with open(log_file_path, 'a', encoding='utf-8') as file:
            file.write(log_message + '\n')

            for attachment in message.attachments:
                file_ext = attachment.filename.split('.')[-1].lower()
                if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'zip', 'rar', 'ico',
                                'txt']:
                    attachment_dir = os.path.join(log_dir, 'attachments')
                    os.makedirs(attachment_dir, exist_ok=True)
                    file_name = f'{time_string}_{sanitize_filename(message.author.name)}_{sanitize_filename(attachment.filename)}'
                    file_path = os.path.join(attachment_dir, file_name)
                    await attachment.save(file_path)
                    file.write(f'{attachment.url} > {file_path}\n')

            for embed in message.embeds:
                embed_log_message = "\nEmbed:"
                embed_log_message += f"\nTitle: {embed.title if embed.title else ''}"
                embed_log_message += f"\nDescription: {embed.description if embed.description else ''}"
                for field in embed.fields:
                    embed_log_message += f"\nField - Name: {field.name if field.name else ''}, Value: {field.value if field.value else ''}"
                embed_log_message += "\n"
                file.write(embed_log_message)

            if message.attachments or message.embeds:
                file.write('\n')

    if config['plugins']:
        for filename in os.listdir(plugins_folder):
            if filename.startswith('on_message_') and filename.endswith('.ext'):
                if __name__ == '__main__':
                    log(f'Loading on message extension {filename}')
                    filepath = os.path.join(plugins_folder, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as file:
                            script = file.read()

                        exec(f"async def plugin_func(bot, message):\n{textwrap.indent(script, '    ')}")
                        await locals()['plugin_func'](bot, message)
                        log(f'Successfully executed: {filename}')
                    except Exception as e:
                        logw(f'Failed to execute {filename}: {e}')


async def example_call_back(interaction):
    await interaction.respond(f'Hello! {interaction.user.mention}, this is an example button!')


async def example_select_menu_callback(interaction: discord.Interaction):
    selected_values = interaction.data['values']
    await interaction.response.send_message(f"You selected: {', '.join(selected_values)}")


async def example_modal_callback(interaction: discord.Interaction, modal: ui.Modal):
    input_1 = modal.children[0].value
    input_2 = modal.children[1].value
    await interaction.response.send_message(f"Received: Input 1 = {input_1}, Input 2 = {input_2}")


eg_button = {
    'label': 'example',
    'style': discord.ButtonStyle.danger,
    'custom_id': 'example',
    'callback': example_call_back,
    'emoji': '🥳'
}
button_configurations.append(eg_button)


@bot.command()
async def example_select_view(ctx: commands.Context):
    options = [
        SelectOption(label="Option 1", value="1"),
        SelectOption(label="Option 2", value="2")
    ]

    view = create_select_view(placeholder="Choose an option", options=options, custom_id="select_menu_1",
                              callback=example_select_menu_callback)
    await ctx.send("Please choose an option:", view=view)


@bot.command()
async def example_modal(ctx: discord.ApplicationContext):
    inputs = [
        discord.ui.InputText(label="Input 1", placeholder="Enter something...", custom_id="input_1"),
        discord.ui.InputText(label="Input 2", placeholder="Enter something else...", custom_id="input_2")
    ]

    modal = create_modal_view(title="Your Modal Title", inputs=inputs, custom_id="modal_1",
                              callback=example_modal_callback)

    await ctx.send_modal(modal)

def register_on_ready_extension(name, data):
    if not os.path.isfile(f'{plugins_folder}/on_ready_{name}.ext'):
        with open(f'{plugins_folder}/on_ready_{name}.ext', 'w') as f:
            f.write(data)


def register_on_message_extension(name, data):
    if not os.path.isfile(f'{plugins_folder}/on_message_{name}.ext'):
        with open(f'{plugins_folder}/on_message_{name}.ext', 'w') as f:
            f.write(data)


if __name__ == '__main__' and config['plugins']:
    if not os.path.exists('plugins'):
        os.mkdir('plugins')
    plugin_files = [f for f in os.listdir('plugins') if os.path.isfile(os.path.join('plugins', f))]
    globals_dict = globals()

    for plugin_file in plugin_files:
        if plugin_file.endswith(".py"):
            plugin_path = os.path.join(plugins_folder, plugin_file)
            with open(plugin_path, encoding='utf-8') as f:
                try:
                    lines = f.readlines()
                    filtered_code = '\n'.join(line for line in lines if not line.strip().startswith('from main import'))

                    code = compile(filtered_code, plugin_path, 'exec')
                    exec(code, globals_dict)
                    log(f'Successfully loaded plugin: {plugin_file}')
                except Exception as e:
                    logerr(f'Error loading plugin: {plugin_file}\n{e}')


@bot.event
async def on_ready():
    for f in when_bot_ready_functions:
        f()
    check_timers.start()
    for button_config in button_configurations:
        button_views[button_config['custom_id']] = create_button_view(
            label=button_config['label'],
            style=button_config['style'],
            custom_id=button_config['custom_id'],
            callback=button_config['callback'],
            emoji=button_config['emoji'] if 'emoji' in button_config else None,
            disabled=button_config['disabled'] if 'disabled' in button_config else False
        )

        bot.add_view(button_views[button_config['custom_id']])

    if config['plugins']:
        if not os.path.exists(plugins_folder):
            os.makedirs(plugins_folder)

        for filename in os.listdir(plugins_folder):
            if filename.startswith('on_ready_') and filename.endswith('.ext'):
                if __name__ == '__main__':
                    log(f'Loading on ready extension {filename}')
                    filepath = os.path.join(plugins_folder, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as file:
                            script = file.read()

                        exec(script)
                        log(f'Loaded: {filename}')
                    except Exception as e:
                        logw(f'Failed to load: {filename}: {e}')


    bot.add_view(CreateTicketView(bot))
    bot.add_view(CloseTicketView(bot))
    bot.add_view(CloseTicketRequestView(bot))
    bot.add_view(DeleteTicketView(bot))

    log(f'Logged in as {bot.user} (ID: {bot.user.id})')

    if not bot.guilds:
        client_id = bot.user.id
        logw(
            f'Bot not in any servers \nOAuth link: https://discord.com/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot')

    log('Starting Post Startup Setup')
    for guild in bot.guilds:
        bot_top_role = guild.get_member(bot.user.id).top_role
        if not any(role.name == "Muted" for role in guild.roles):
            log(f"Creating 'Muted' role in guild {guild}")
            permissions = discord.Permissions(send_messages=False, speak=False)
            mute_role = await guild.create_role(name="Muted", permissions=permissions)
            try:
                if mute_role.position >= bot_top_role.position:
                    raise discord.HTTPException(None, "Role hierarchy issue")
                await mute_role.edit(position=bot_top_role.position - 1)
            except discord.HTTPException as e:
                logw(f"Failed to move 'Muted' role in {guild.name}: {e}")
                log("Retrying hierarchy adjustment...")
                bot_controlled_roles = [role for role in guild.roles if role.managed]
                for role in bot_controlled_roles:
                    if role.position >= bot_top_role.position:
                        await role.edit(position=bot_top_role.position - 1)
            for channel in guild.channels:
                log(f"Setting 'Muted' permissions in guild {guild} channel {channel}")
                try:
                    await channel.set_permissions(mute_role, send_messages=False, speak=False)
                except Exception as e:
                    logw(e)
        if not server_configs.get(str(guild.id)):
            server_configs[str(guild.id)] = {}

        server_config = server_configs.get(str(guild.id))
        if server_config:
            if server_config.get('member_count_channel'):
                channel = bot.get_channel(int(server_config.get('member_count_channel')))
                if not channel:
                    server_configs[str(guild.id)]['member_count_channel'] = None
                    save_server_configs(server_configs)
                else:
                    member_count = len(channel.guild.members)
                    await channel.edit(name=f'Members: {member_count}')

    await bot.sync_commands()

    log('Post Startup Finished!')


when_bot_join_guild_functions = []
def when_bot_join_guild(function):
    when_bot_join_guild_functions.append(function)
    return function


@bot.event
async def on_guild_join(guild):
    for function in when_bot_join_guild_functions:
        function(guild)

    bot_top_role = guild.get_member(bot.user.id).top_role
    if not any(role.name == "Muted" for role in guild.roles):
        log(f"Creating 'Muted' role in guild {guild}")
        permissions = discord.Permissions(send_messages=False, speak=False)
        mute_role = await guild.create_role(name="Muted", permissions=permissions)
        try:
            if mute_role.position >= bot_top_role.position:
                raise discord.HTTPException(None, "Role hierarchy issue")
            await mute_role.edit(position=bot_top_role.position - 1)
        except discord.HTTPException as e:
            logw(f"Failed to move 'Muted' role in {guild.name}: {e}")
            log("Retrying hierarchy adjustment...")
            bot_controlled_roles = [role for role in guild.roles if role.managed]
            for role in bot_controlled_roles:
                if role.position >= bot_top_role.position:
                    await role.edit(position=bot_top_role.position - 1)
        for channel in guild.channels:
            log(f"Setting 'Muted' permissions in guild {guild} channel {channel}")
            try:
                await channel.set_permissions(mute_role, send_messages=False, speak=False)
            except Exception as e:
                logw(e)
    if not server_configs.get(str(guild.id)):
        server_configs[str(guild.id)] = {}


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
    time.sleep(2)
    restart_bot()
"""
    with open("restart_script.py", "w") as f:
        f.write(script_content)
    log("Restart script created.")


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
    logger.info("Bot is shutting down...")
    await bot.close()


async def restart_bot():
    logger.info("Bot is restarting...")
    subprocess.Popen(["python", "restart_script.py"])
    await bot.close()


def signal_handler(sig, frame):
    logger.info(f'Received signal {sig}. Exiting gracefully...')
    asyncio.create_task(save_state_and_exit())


atexit.register(lambda: asyncio.run(save_state_and_exit()))
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


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


if __name__ == '__main__':
    run_bot()
