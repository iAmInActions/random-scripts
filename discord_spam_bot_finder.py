#!/usr/bin/python3

# Discord Spam self-bot mitigation script
# written by mueller_minki in 2024
#
# Setup:
# 1: Add a role called "Certified Spam" or whatever you want to call it to your server.
# 2: Put your bot token, guild id and channel id into the configuration section.
# 3: If you have a self-roles selector, add your spam role as a button with a disclaimer
#    for normal users that pressing it will result in being spam flagged.
# 4: Mark as executable (chmod +x) and launch the python script.

# Import libraries (you need to install the discord library with "pip3 install discord")
import discord
import asyncio
from datetime import datetime, timedelta
from discord.ext import tasks

# CONFIGURATION SECTION
TOKEN = 'B0T.T0K3N.G03S.H3R3' # Update with your bot token
guild_id = 1234567890  # Update with your guild ID
channel_id = 1234567890  # Update with your staff-only log channel ID
spam_role_name = "Certified Spam" # Adjust if you want to name the role differently

# -- Code starting here, there should be no need to modify any of this --

# Define the intents your bot will use
intents = discord.Intents.default()
intents.members = True  # Enable the members intent
intents.messages = True  # Enable the message content intent
intents.guild_messages = True  # Enable the message content intent
intents.message_content = True  # Enable the message content intent

# Initialize the Discord client with intents
client = discord.Client(intents=intents)

# Define global variables
guild = None
channel = None
role = None
user_messages = {}  # Define user_messages dictionary

@client.event
async def on_ready():
    global guild, channel, role
    print('Logged in as {0.user}'.format(client))
    guild = client.get_guild(guild_id)
    channel = guild.get_channel(channel_id)
    role = discord.utils.get(guild.roles, name=spam_role_name)
    check_spam_role_and_timeout.start()

@tasks.loop(minutes=30)
async def check_spam_role_and_timeout():
    global guild, channel, role, user_messages
    user_messages.clear()  # Clear user_messages dictionary
    if role is None:
        await channel.send(f"Role '{spam_role_name}' not found.")
        return

    # Get all members who have the role but are not timed out
    members_with_role = [member for member in guild.members if role in member.roles and not any(role.name == "Certified Spam" for role in member.roles)]
    if members_with_role:
        timeout_message = "Users with the 'Certified Spam' role:"
        for member in members_with_role:
            timeout_message += f"\n{member.display_name}"
            # Apply timeout for 1 day
            await member.timeout(datetime.utcnow() + timedelta(days=1), reason="Certified Spam")
        await channel.send(timeout_message)
    else:
        print("No users with the 'Certified Spam' role found who are not timed out.")

@client.event
async def on_message(message):
    global guild, channel, role, user_messages
    if message.author.bot:  # Ignore messages from bots
        return

    if len(message.content) > 8:  # Check if message length is greater than 8 characters
        user_id = message.author.id
        current_time = datetime.utcnow()

        # Check if user has sent a message in another channel within the last 2 minutes
        if user_id in user_messages:
            for prev_message_data in user_messages[user_id]:
                prev_message = prev_message_data['message']
                if (current_time - prev_message_data['time']).total_seconds() <= 120 and prev_message.content == message.content:
                    # Send the removed message to the specified channel
                    removed_message = f"{message.author.display_name} has posted potential spam:\n{message.content}"
                    await channel.send(removed_message)
                    print(removed_message)
                    
                    # Delete the messages
                    await message.delete()
                    await prev_message.delete()
                    
                    # Apply the "Certified Spam" role to the user
                    await message.author.add_roles(role, reason="Repeated spam message")
                    await message.author.timeout(discord.utils.utcnow() + timedelta(days=1), reason="Repeated spam message")
                    break  # No need to continue checking

        # Update user's recent messages
        if user_id not in user_messages:
            user_messages[user_id] = []
        user_messages[user_id].append({'message': message, 'content': message.content, 'time': current_time})

        # Remove older messages (more than 2 minutes old)
        user_messages[user_id] = [msg for msg in user_messages[user_id] if (current_time - msg['time']).total_seconds() <= 120]


# Run the bot with the provided token
client.run(TOKEN)

