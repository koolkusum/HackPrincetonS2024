# https://discord.com/oauth2/authorize?client_id=1223585350467719198&permissions=21983791152192&scope=bot

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import random
import datetime

import regular_response
import user_response
import task_response
from user import User, UserDatabase

load_dotenv()

def run_discord_bot():
    TOKEN = os.getenv('DISCORD_TOKEN')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)
    userDatabase = UserDatabase('user_database.db')
    
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')
        client.loop.create_task(ping_at_specific_time(client))
    
    @client.event
    async def on_message(message : discord.message.Message):
        if message.author == client.user:
            return
        username = str(message.author)
        mention = str(message.author.mention)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f'{username} ({mention}) said: "{user_message}" ({channel})')

        if client.user.mentioned_in(message):
            message_content = str(message.content)
            parts = message_content.split()
            if len(parts) >= 2:
                command = parts[1]
                message.content = command
            if message.content.startswith('!'):
                await process_command(message, client)
    
    async def ping_at_specific_time(client : discord.Client):
        while True:            
            userDatabase = UserDatabase('user_database.db')
            user_list = userDatabase.get_all_users()
            current_time = datetime.datetime.now().strftime("%H:%M")
            for user_index in user_list:
                if current_time == user_index[2]:
                    print(f'{current_time} BOT PINGED')
                    user = await client.fetch_user(user_index[1])
                    tasks_list = userDatabase.get_tasks_by_id(user_index[1])
                    def convert_to_datetime(date_str):
                        try:
                            return datetime.datetime.strptime(date_str, "%Y%m%dT%H:%M:%S")
                        except ValueError:
                            print(f"Error: Invalid date string encountered: {date_str}")
                            return None
                    today_date = datetime.datetime.today().date()
                    today_tasks = [task for task in tasks_list if convert_to_datetime(task[3]).date() == today_date]
                    sorted_data = sorted(today_tasks, key=lambda x: convert_to_datetime(x[3]))
                    result_title = f'**Today Tasks:**'
                    result_description = f'**{user_index[0]}\'s tasks**'
                    embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                    file = discord.File('static/Images/icon.png', filename='icon.png')
                    embed.set_thumbnail(url='attachment://icon.png')
                    embed.set_author(name="HackPrinceton2024-Bot says:")
                    print(len(today_tasks))
                    if len(today_tasks) > 0:
                        for item in sorted_data:
                            string = f'{item[2]} to {item[3]}'
                            embed.add_field(name=item[1], value=string, inline=False)
                    else:
                            embed.add_field(name="No Tasks Schedule for Today", value="Have a Great Day!", inline=False)
                    embed.set_footer(text=client.user.mention)
                    await user.send(file=file, embed=embed)
            userDatabase.close()
            await asyncio.sleep(60)

    async def process_command(message : discord.message.Message, client : discord.Client):
        userDatabase = UserDatabase('user_database.db')
        if message.content == '!hello':
            await regular_response.hello(message)
        elif message.content == '!time':
            await regular_response.time(message)
        elif message.content == '!adduser':
            await user_response.adduser(message, client, userDatabase)
        elif message.content == '!userinfo':
            await user_response.userinfo(message, client, userDatabase)
        elif message.content == '!changereminder':
            await user_response.changereminder(message, client, userDatabase)
        elif message.content == '!deleteuser':
            await user_response.deleteuser(message, client, userDatabase)
        elif message.content == '!addtask':
            await task_response.addtask(message, client, userDatabase)
        elif message.content == '!todaytask':
            await task_response.todaytask(message, client, userDatabase)
        elif message.content == '!alltasks':
            await task_response.alltask(message, client, userDatabase)
        elif message.content == '!removetask':
            await task_response.removetask(message, client, userDatabase)
        elif message.content == '!completetask':
            await task_response.completetask(message, client, userDatabase)
        elif message.content == '!pomodoro':
            await regular_response.pomodoro(message, client)
        elif message.content == '!help':
            await regular_response.help(message, client)
        else:
            await regular_response.invalidInput(message, client)
        userDatabase.close()

    client.run(TOKEN)
    
if __name__ == '__main__':
    run_discord_bot()