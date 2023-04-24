current_version = 'V5.1'
current_config_format = '3'

import discord
import json
import os
import tkinter as tk
import random as rand
import time

from datetime import datetime
from datetime import timedelta
from github import Github
from discord import Status
from tkinter import messagebox
from discord.ext import commands
from discord.utils import get

# Load or save bot configuration from BotConfig.json file

if not os.path.isfile('BotConfig.json'):
    print('No config file found creating BotConfig.json')
    INPUT_PREFIX= input('\nWhat do you want the bot prefix to be? \n')
    INPUT_BOT_TOKEN= input('\nEnter bot token. \n')
    INPUT_WELCOME_CHANNEL_ID= input('\nEnter welcome channel ID. \n')
    INPUT_OWNER_ID= input("\nEnter owner's ID.\n")
    INPUT_OWNER_NAME= input("\nEnter owner's name.\n")
    INPUT_OWNER_ROLE_NAME= input("\nEnter owner role name.\n")
    INPUT_MOD_ROLE_NAME= input("\nEnter MOD role name.\n")
    INPUT_WIN_PROB= input("\nEnter win probabilaty for coinflip. (eg 0.55 means 55%)\n")
    INPUT_INTREST_RATE= input("\nEnter intrest rate for loan. (eg 0.05 means 5%)\n")

    QUESTION = input("\nDoes your server have custom member role? (YESY/NO)\n")
    if QUESTION.lower() == 'yes':
        INPUT_MEMBER_ROLE_NAME= input("\nEnter member role name\n")
    else:
        INPUT_MEMBER_ROLE_NAME= None

    QUESTION = input("\nDoes your server need Member count? (YESY/NO)\n")
    if QUESTION.lower() == 'yes':
        INPUT_MEMBER_COUNT_ID= input("\nEnter member count channel ID\n")
    else:
        INPUT_MEMBER_COUNT_ID= None
    config = {
        'config_format': current_config_format,
        'prefix': INPUT_PREFIX,
        'bot_token': INPUT_BOT_TOKEN,
        'welcome_channel': INPUT_WELCOME_CHANNEL_ID,
        'owner_id': INPUT_OWNER_ID,
        'owner_name': INPUT_OWNER_NAME,
        'owner_role': INPUT_OWNER_ROLE_NAME,
        'mod_role': INPUT_MOD_ROLE_NAME,
        'member_role': INPUT_MEMBER_ROLE_NAME,
        'win_prob': INPUT_WIN_PROB,
        'intrest_rate': INPUT_INTREST_RATE,
        'member_count_id': INPUT_MEMBER_COUNT_ID,
        'debug': 'False'
    }
    with open('BotConfig.json', 'w') as f:
        f.write(json.dumps(config, indent=4, ensure_ascii=False, separators=(',', ': ')) + '\n')
    messagebox.showinfo(title="Va's BOT", message="Please restart the app", icon=messagebox.INFO)
else:

    with open('BotConfig.json') as f:
        config = json.load(f)

    bot = commands.Bot(command_prefix=config['prefix'], intents=discord.Intents.all())
    try:
        config_format = config['config_format']
    except:
        messagebox.showinfo(title="Va's BOT", message="Please Regenerate Config file", icon=messagebox.INFO)
    if config_format != current_config_format:
      messagebox.showinfo(title="Va's BOT", message="Please Regenerate Config file", icon=messagebox.INFO)          

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        debug = config['debug']
        print(f'Debug: {debug}')
        if config['member_count_id'] != None:
            channel = bot.get_channel(int(config['member_count_id']))
            member_count = len(channel.guild.members)
            await channel.edit(name=f'Members: {member_count}')

    @bot.event
    async def on_member_join(member):
        ID = int(config['welcome_channel'])
        channel = bot.get_channel(1096103887188021248) # Replace channel_id with the ID of the channel you want the bot to send the message in
        await channel.send(f'Welcome to the server, {member.mention}!')
        if config['debug'] == True:
            print(ID)
            print(bot.get_all_channels())
        if config['member_count_id'] != None:
            channel = bot.get_channel(int(config['member_count_id']))
            member_count = len(channel.guild.members)
            await channel.edit(name=f'Members: {member_count}')

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
    async def aboutme(ctx):
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
    async def setstatus(ctx, status_type: str, *, status_text: str):
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
    async def clearstatus(ctx):
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
    @bot.command()
    @has_required_perm() # decorator to ensure user has necessary permissions
    async def createrole(ctx, role_name):
        try:
            guild = ctx.guild
            permissions = discord.Permissions(send_messages=True, read_messages=True) # set desired permissions for the role
            await guild.create_role(name=role_name, permissions=permissions) # create the role
            await ctx.send(f"Role {role_name} has been created.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    @bot.command()
    @has_required_perm() # decorator to ensure user has necessary permissions
    async def deleterole(ctx, role: discord.Role):
        try:
            await role.delete() # delete the role
            await ctx.send(f"Role {role.name} has been deleted.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
    @bot.command()
    @has_required_perm() # decorator to ensure user has necessary permissions
    async def changerolecolor(ctx, role: discord.Role, hex_color: str):
        try:
            color = discord.Colour(int(hex_color.strip("#"), 16)) # convert hex color string to a discord.Color object
            await role.edit(colour=color) # update the color of the role
            await ctx.send(f"Color of role {role.name} has been changed.")
        except ValueError:
            await ctx.send("Invalid color format. Please enter a valid hex color code (e.g. #FF0000).")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")


    # Check if balances.json file exists, create it if it doesn't
    if not os.path.exists("balances.json"):
        with open("balances.json", "w") as f:
            json.dump({}, f)

    # Load balances from JSON file
    with open("balances.json", "r") as f:
        balances = json.load(f)
    last_claim_times = {}


    # Register command
    @bot.command()
    async def register(ctx):
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 100
            with open("balances.json", "w") as f:
                f.write(json.dumps(balances) + '\n')
            await ctx.send(f"{ctx.author.mention}, you have been registered with a starting balance of 100 coins.")
        else:
            await ctx.send(f"{ctx.author.mention}, you are already registered.")

    # Give command
    @bot.command()
    async def give(ctx, recipient: discord.Member, amount: int):
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
    # Coinflip command
    # Coinflip command with pre-defined win probability

    win_prob = float(config['win_prob'])
    
    @bot.command()
    async def cf(ctx, bet: int):
        user_id = str(ctx.author.id)
        if user_id not in balances:
            await ctx.send(f"{ctx.author.mention}, you are not registered.")
        elif balances[user_id] < bet:
            await ctx.send(f"{ctx.author.mention}, you do not have enough coins.")
        elif bet < 1:
            await ctx.send(f"{ctx.author.mention}, you cant bet a number lower than 1")
        else:
            # Define win probability

            # Calculate win or loss
            if rand.random() < win_prob:
                balances[user_id] += bet
                result = f"won {bet} coins! 😃"
            else:
                balances[user_id] -= bet
                result = f"lost {bet} coins. 😞"
            with open("balances.json", "w") as f:
                json.dump(balances, f)
            await ctx.send(f"{ctx.author.mention}, you {result} Your balance is now {balances[user_id]} coins.")




    # Bal command
    @bot.command()
    async def bal(ctx):
        user_id = str(ctx.author.id)
        if user_id not in balances:
            await ctx.send(f"{ctx.author.mention}, you are not registered.")
        else:
            user_bal = balances[user_id]
            await ctx.send(f"{ctx.author.mention}, your balance is {user_bal} coins.")


    # Leaderboard command
    @bot.command()
    async def lb(ctx):
        sorted_balances = {k: v for k, v in sorted(balances.items(), key=lambda item: item[1], reverse=True)}
        leaderboard = "```"
        leaderboard += "LEADERBOARD\n"
        leaderboard += "-----------\n"
        for i, (user_id, balance) in enumerate(sorted_balances.items()):
            user = await bot.fetch_user(int(user_id))
            leaderboard += f"{i+1}. {user.name}#{user.discriminator}: {balance} coins\n"
        leaderboard += "```"
        await ctx.send(leaderboard)
    
    @bot.command()
    @has_required_perm()
    async def reset(ctx, member: discord.Member):
        user = str(member.id)

        # Reset the balance for the member
        with open("balances.json", "r") as f:
            players = json.load(f)
        if user not in players:
            await ctx.send("This user does not have a player account.")
            return
        players[user] = 0
        with open("balances.json", "w") as f:
            json.dump(players, f)
        await ctx.send(f"{member.display_name}'s account has been reset to 0 coins.")

        # Reset the claim data for the member
        with open("daily_claims.json", "r") as f:
            claims = json.load(f)
        if user in claims:
            del claims[user]
        with open("daily_claims.json", "w") as f:
            json.dump(claims, f)

        # Reload the data
        with open("balances.json", "r") as f:
            balances = json.load(f)
        with open("daily_claims.json", "r") as f:
            last_claim_times = json.load(f)
    @bot.command()
    async def daily(ctx):
        user_id = str(ctx.author.id)
        current_time = time.time()

        if user_id not in balances:
            await ctx.send(f"{ctx.author.mention}, you are not registered.")

        # Load the previous claims data from file if it exists
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
            reward = rand.randint(100, 1000)
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
            await ctx.send(f"Sorry {ctx.author.mention}, you can claim your daily reward again in {hours} hours, {minutes} minutes, and {seconds} seconds.")

        # Save the updated claims data to file
        with open('daily_claims.json', 'w') as f:
            json.dump(last_claim_times, f)
        with open('balances.json', 'w') as f:
            json.dump(balances, f)
    if not os.path.isfile('loan_data.json'):
        with open('loan_data.json', 'w') as f:
            json.dump({}, f)
    @bot.command()
    async def loan(ctx):
        user_id = str(ctx.author.id)
        current_time = time.time()

        if user_id not in balances:
            await ctx.send(f"{ctx.author.mention}, you are not registered.")
            return

        # Load the previous loan data from file if it exists
        if os.path.isfile('loan_data.json'):
            with open('loan_data.json', 'r') as f:
                loan_data = json.load(f)
        else:
            loan_data = {}

        # Check if the user has an existing loan
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
                # Reset user's balance if loan not repaid after 24 hours
                if time_since_loan >= 172800:
                    balances[user_id] = 0
                    await ctx.send(f"Sorry {ctx.author.mention}, your balance has been reset as you have failed to repay your loan in time.")
                del loan_data[user_id]

        # Allow user to take loan
        amount = 1000
        balances[user_id] += amount
        loan_data[user_id] = {'time': current_time, 'amount': amount}

        # Save the updated loan data to file
        with open('loan_data.json', 'w') as f:
            json.dump(loan_data, f)

        # Save the updated balances data to file
        with open('balances.json', 'w') as f:
            json.dump(balances, f)

        await ctx.send(f"{ctx.author.mention}, you have taken a loan of {amount} coins. Please repay it within 24 hours.")


    @bot.command()
    async def returnloan(ctx):
        user_id = str(ctx.author.id)
        current_time = time.time()

        if user_id not in balances:
            await ctx.send(f"{ctx.author.mention}, you are not registered.")
            return

        # Load the previous loan data from file if it exists
        with open('loan_data.json', 'r') as f:
            loan_data = json.load(f)
        if user_id not in loan_data:
            await ctx.send(f"{ctx.author.mention}, you do not have any outstanding loan.")
            return

        # Calculate interest and update balance
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

            # Update loan data
            del loan_data[user_id]
            with open('loan_data.json', 'w') as f:
                json.dump(loan_data, f)
            with open('balances.json', 'w') as f:
                json.dump(balances, f)

            await ctx.send(f"{ctx.author.mention}, you have returned {total_amount} coins, including {interest} coins of interest. Your new balance is {balances[user_id]} coins.")



    @bot.command()
    @has_required_perm()
    async def loadloans(ctx):
        # Load the loan data from file
        with open('loan_data.json', 'r') as f:
            loan_data = json.load(f)

        # Update user balances
        for user_id in loan_data.keys():
            balances[user_id] += loan_data[user_id]

        await ctx.send(f"Loans have been loaded from file and applied to user balances.")
    


    

    









    














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
            `{prefix}aboutme` - Tells you a few things about your user ID.
            `{prefix}random <min> <max>` - Gives you a random number.
            `{prefix}register` - Register a account for currency.
            `{prefix}cf <value>` - Coin flips and decides what you won or lose.
            `{prefix}daily` - Claims daily reward.
            `{prefix}lb` - Shows leaderboard
            `{prefix}loan` - Gives a lone of 500 coins.
            `{prefix}returnloan` - Returns loan if taken.
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
            `{prefix}setstatus` - Custom Status.
            `{prefix}clearstatus` - Clears Custom Status.
            `{prefix}shutdown` - Shutsdown the bot''')
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
            `{prefix}createrole <value>` - Creates a role.
            `{prefix}deleterole <value>` - Deletes a role.
            `{prefix}changerolecolor <valuse> <hex value>` - Changes role colour.
            `{prefix}reset <member>` - Resets account of a member
            For More Info Contact <@{owner.id}>''')
            await ctx.send(help_msg)


    def check_for_updates():
        # Set your Github access token as an environment variable
        ACCESS_TOKEN = os.environ.get('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')
        # Set the repository name and owner
        REPO_NAME = 'VA-S-BOT'
        REPO_OWNER = 'DEAMJAVA'
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
