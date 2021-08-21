# bot.py
import os

import discord
import random
from discord.ext import commands, tasks
from dotenv import load_dotenv
import osrs
import logging
import status

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.command(name='dm', help='Test dm functionality')
async def dm(ctx):
    await ctx.author.send('Hello!')

@bot.command(name='getlevels', help='Gets the given accounts skill levels.')
async def get_levels(ctx, *account_name):
    username = ' '.join(account_name)
    print('Recieved command to getlevels of %s' % username)
    s = osrs.get_account_skills_message(username)
    s = '```'+s+'```'
    await ctx.send(s)

@bot.command(name='follow', help='Adds the user as a follower of the given osrs account')
async def follow(ctx, *account_name):
    username = ' '.join(account_name)
    response = osrs.add_account_follower(username.lower(), ctx.author.id)
    message = {
        status.SUCCESS: f'You are now following {username}.',
        status.ACCOUNT_DOES_NOT_EXIST: f'The account {username} does not exist.',
        status.ALREADY_FOLLOWING: f'You are already following {username}.'
    }
    await ctx.author.send(message.get(response, 'Error.'))

@bot.command(name='unfollow', help='Removes the user as a follower of the given osrs account')
async def unfollow(ctx, *account_name):
    username = ' '.join(account_name)
    response = osrs.remove_account_follower(username.lower(), ctx.author.id)
    message = {
        status.SUCCESS: f'You have unfollowed {username}.',
        status.ACCOUNT_NOT_IN_DB: f'You were not following {username}.',
        status.ALREADY_FOLLOWING: f'You were not following {username}.'
    }
    print(message.get(response, 'Error.'))
    await ctx.author.send(message.get(response, 'Error.'))

@tasks.loop(seconds=300) # 5 minutes
async def send_message():
    updates = osrs.update_tuples()
    for update in updates:
        for follower_id in update[1]:
            user = await bot.fetch_user(follower_id)
            await user.send('```'+update[0]+'```')

    # user = await bot.fetch_user(184861883767980032)
    # await user.send("Hi!")

# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.errors.CheckFailure):
#         await ctx.send('You do not have the correct role for this command.')
send_message.start()

bot.run(TOKEN)
