import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import random
import datetime
import regex as re

from google.auth import load_credentials_from_file
from google.oauth2 import credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.generativeai import generative_models
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

from user import User, UserDatabase

async def addtask(message : discord.message.Message, client : discord.Client, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(message.author.id)):
        result_title = f'**Name of the task you want to enter**'
        result_description = f'**Please enter the name of the task**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        embed.set_footer(text="!addtask")
        await message.channel.send(file=file, embed=embed)
        def check(m):
            return m.author == message.author and m.channel == message.channel
        addtask_action = await client.wait_for('message', check=check, timeout=30)
        try:
            addtask_action_content = addtask_action.content            
        except asyncio.TimeoutError:
            # await message.channel.send(f'{message.author.mention} has taken too long to respond.')
            string = f'{message.author.mention} has taken too long to respond.'
            embed = discord.Embed(title= "Timeout Error", description=string, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            embed.set_footer(text="!addtask")
            await message.channel.send(file=file, embed=embed)
            return

        result_title = f'**Task Start Time**'
        result_description = f'What time does this task start?**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        embed.add_field(name="Please enter in {YEAR}-{MONTH}-{DAY}T{HOUR}:{MINUTE}:{SECOND}", value="EXAMPLE: 2024-03-25T16:45:00")
        embed.set_footer(text="!addtask")
        await message.channel.send(file=file, embed=embed)
        def check(m):
            return m.author == message.author and m.channel == message.channel
        addtask_start_action = await client.wait_for('message', check=check, timeout=30)
        try:
            addtask_start_action_content = addtask_start_action.content
            def validate_time(time_str):
                pattern = r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})$'
                match = re.match(pattern, time_str)                
                if not match:
                    return False
                year, month, day, hour, minute, second = map(int, match.groups())
                if not (1 <= month <= 12 and 1 <= day <= 31 and 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                    return False
                if month == 2 and day > 28:
                    return False                
                return True
            check = validate_time(addtask_start_action_content)
            if not check:
                result_title = f'Invalid Output'
                result_description = f'Time should be in **YEAR-MONTH-DATETHOUR:MINUTE:SECONDS** format for **{message.author.mention}**'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('static/Images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="HackPrinceton2024-Bot says:")
                embed.add_field(name="Please enter in {YEAR}-{MONTH}-{DAY}T{HOUR}:{MINUTE}:{SECOND}", value="EXAMPLE: 2024-03-25T16:45:00")
                embed.set_footer(text="!changereminder")
                await message.channel.send(file=file, embed=embed)
                return
            
        except asyncio.TimeoutError:
            string = f'{message.author.mention} has taken too long to respond.'
            embed = discord.Embed(title= "Timeout Error", description=string, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            embed.set_footer(text="!addtask")
            await message.channel.send(file=file, embed=embed)
            return
        
        result_title = f'**Task End Time**'
        result_description = f'What time does this task end?**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        embed.add_field(name="Please enter in {YEAR}-{MONTH}-{DAY}T{HOUR}:{MINUTE}:{SECOND}", value="EXAMPLE: 2024-03-25T16:45:00")
        embed.set_footer(text="!addtask")
        await message.channel.send(file=file, embed=embed)
        def check(m):
            return m.author == message.author and m.channel == message.channel
        addtask_end_action = await client.wait_for('message', check=check, timeout=30)
        try:
            addtask_end_action_content = addtask_end_action.content
            def validate_time(time_str):
                pattern = r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})$'
                match = re.match(pattern, time_str)                
                if not match:
                    return False
                year, month, day, hour, minute, second = map(int, match.groups())
                if not (1 <= month <= 12 and 1 <= day <= 31 and 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
                    return False
                if month == 2 and day > 28:
                    return False                
                return True
            check = validate_time(addtask_end_action_content)
            if not check:
                result_title = f'Invalid Output'
                result_description = f'Time should be in **YEARMONTHDATETHOUR:MINUTE:SECONDS** format for **{message.author.mention}**'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('static/Images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="HackPrinceton2024-Bot says:")
                embed.add_field(name="Please enter in {YEAR}-{MONTH}-{DAY}T{HOUR}:{MINUTE}:{SECOND}", value="EXAMPLE: 2024-03-25T16:45:00")
                embed.set_footer(text="!changereminder")
                await message.channel.send(file=file, embed=embed)
                return
            
        except asyncio.TimeoutError:
            string = f'{message.author.mention} has taken too long to respond.'
            embed = discord.Embed(title= "Timeout Error", description=string, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            embed.set_footer(text="!addtask")
            await message.channel.send(file=file, embed=embed)
            return
        
        local_time = datetime.datetime.now()
        local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        current_time = datetime.datetime.now(local_timezone)
        timezone_offset = current_time.strftime('%z')
        offset_string = list(timezone_offset)
        offset_string.insert(3, ':')
        timeZone = "".join(offset_string)
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)        

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists("token.json"):
                        os.remove("token.json")
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port = 0)

                with open("token.json", "w") as token:
                    token.write(creds.to_json())
        service = build("calendar", "v3", credentials = creds)
        now = datetime.datetime.now().isoformat() + "Z"
        datetime_stuff = datetime.datetime.now()
        today_date = f'{datetime_stuff.year}-{datetime_stuff.month}-{datetime_stuff.day}T'
        event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()
        taskSummary = addtask_action_content
        taskStart = addtask_start_action_content
        taskEnd = addtask_end_action_content
        event = {
            'summary': taskSummary,
            'start': {
                'dateTime': taskStart,
                'timeZone': 'America/New_York',
            },
            'end': {
                'dateTime': taskEnd,
                'timeZone': 'America/New_York',
            },
        }
        event = service.events().insert(calendarId = "primary", body = event).execute()
        print(f"Event Created {event.get('htmlLink')}")

        userDatabase.add_task(str(message.author.id), addtask_action_content, addtask_start_action_content, addtask_end_action_content)
        result_title = f'**Task Created**'
        result_description = 'Task Description:'

        description = userDatabase.get_task_by_name(addtask_action_content)
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        embed.add_field(name="Task Name", value=description[1], inline=False)
        embed.add_field(name="Task Start Date", value=description[2], inline=False)
        embed.add_field(name="Task End Date", value=description[3], inline=False)
        complete = True
        if description[4] == 0:
            complete = False        
        embed.add_field(name="Task Completed", value=complete, inline=False)
        embed.set_footer(text="!addtask")
        await message.channel.send(file=file, embed=embed)
    else:
        result_title = f'Account Not Found'
        result_description = f'User not found for for **{message.author.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        embed.set_footer(text="!addtask")
        await message.channel.send(file=file, embed=embed)
            
async def todaytask(message : discord.message.Message, client : discord.Client, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(message.author.id)):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)        

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists("token.json"):
                        os.remove("token.json")
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port = 0)

                with open("token.json", "w") as token:
                    token.write(creds.to_json())
        service = build("calendar", "v3", credentials = creds)
        now = datetime.datetime.now().isoformat() + "Z"
        event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()

        events = event_result.get("items", [])
        data = userDatabase.get_tasks_by_id(str(message.author.id))
        if not events:
            print("No upcoming events found!")
        else:
            discord_id = str(message.author.id)    
            tasks_names = userDatabase.get_task_names_by_id(discord_id)
            for event in events:
                event_name = event['summary'].replace('"', '')
                event_start = event['start']['dateTime'][:19]
                event_end = event['end']['dateTime'][:19]       
                if event_name not in tasks_names:
                    userDatabase.add_task(str(message.author.id), event_name, event_start, event_end, False)
        data = userDatabase.get_tasks_by_id(str(message.author.id))
        def convert_to_datetime(date_str):
            try:
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                print(f"Error: Invalid date string encountered: {date_str}")
                return None
        today_date = datetime.datetime.today().date()
        today_tasks = [task for task in data if convert_to_datetime(task[3]).date() == today_date]
        sorted_data = sorted(today_tasks, key=lambda x: convert_to_datetime(x[3]))
        result_title = f'**Today Tasks:**'
        result_description = f'**{message.author.mention}\'s tasks**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        for item in sorted_data:
            string = f'{item[2]} to {item[3]}'
            embed.add_field(name=item[1], value=string, inline=False)
        embed.set_footer(text="!todaytask")
        await message.channel.send(file=file, embed=embed)
    else:
        result_title = f'Account Not Found'
        result_description = f'User not found for for **{message.author.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        embed.set_footer(text="!todaytask")
        await message.channel.send(file=file, embed=embed)

async def alltask(message : discord.message.Message, client : discord.Client, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(message.author.id)):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)        

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists("token.json"):
                        os.remove("token.json")
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port = 0)

                with open("token.json", "w") as token:
                    token.write(creds.to_json())
        service = build("calendar", "v3", credentials = creds)
        now = datetime.datetime.now().isoformat() + "Z"
        event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()

        events = event_result.get("items", [])
        data = userDatabase.get_tasks_by_id(str(message.author.id))
        if not events:
            print("No upcoming events found!")
        else:
            discord_id = str(message.author.id)    
            tasks_names = userDatabase.get_task_names_by_id(discord_id)
            for event in events:
                event_name = event['summary'].replace('"', '')
                event_start = event['start']['dateTime'][:19]
                event_end = event['end']['dateTime'][:19]       
                if event_name not in tasks_names:
                    userDatabase.add_task(str(message.author.id), event_name, event_start, event_end, False)
        data = userDatabase.get_tasks_by_id(str(message.author.id))
        if len(data) == 0:
            result_title = f'**All Tasks:**'
            result_description = f'**{message.author.mention}\'s tasks**'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            embed.add_field(name="No Tasks Scheduled! Have a great day!", value="Congrats!")
            embed.set_footer(text="!alltasks")
        else:
            def convert_to_datetime(date_str):
                try:
                    return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    print(f"Error: Invalid date string encountered: {date_str}")
                    return None
            all_tasks = [task for task in data if task[4] == False]
            sorted_data = sorted(all_tasks, key=lambda x: convert_to_datetime(x[3]))
            result_title = f'**All Tasks:**'
            result_description = f'**{message.author.mention}\'s tasks**'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            for item in sorted_data:
                string = f'{item[2]} to {item[3]}'
                embed.add_field(name=item[1], value=string, inline=False)
            embed.set_footer(text="!alltasks")
        await message.channel.send(file=file, embed=embed)
    else:
        result_title = f'Account Not Found'
        result_description = f'User not found for for **{message.author.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        embed.set_footer(text="!alltasks")
        await message.channel.send(file=file, embed=embed)

async def removetask(message : discord.message.Message, client : discord.Client, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(message.author.id)):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)        

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists("token.json"):
                        os.remove("token.json")
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port = 0)

                with open("token.json", "w") as token:
                    token.write(creds.to_json())
        service = build("calendar", "v3", credentials = creds)
        now = datetime.datetime.now().isoformat() + "Z"
        event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()
        events = event_result.get("items", [])
        data = userDatabase.get_tasks_by_id(str(message.author.id))
        if not events:
            print("No upcoming events found!")
        else:
            discord_id = str(message.author.id)    
            tasks_names = userDatabase.get_task_names_by_id(discord_id)
            for event in events:
                event_name = event['summary'].replace('"', '')
                event_start = event['start']['dateTime'][:19]
                event_end = event['end']['dateTime'][:19]       
                if event_name not in tasks_names:
                    userDatabase.add_task(str(message.author.id), event_name, event_start, event_end, False)
        data = userDatabase.get_tasks_by_id(str(message.author.id))
        listTasks = userDatabase.get_tasks_by_id(str(message.author.id))
        result_title = f'**Name of the task you want to delete**'
        result_description = f'**Please enter the name of the task**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        for i in listTasks:
            string = f'{i[2]} to {i[3]}'
            embed.add_field(name=i[1], value=string, inline=False)
        embed.set_footer(text="!removetask")
        await message.channel.send(file=file, embed=embed)
        def check(m):
            return m.author == message.author and m.channel == message.channel
        removedtask_action = await client.wait_for('message', check=check, timeout=30)
        try:
            removetask_action_content = removedtask_action.content            
        except asyncio.TimeoutError:
            string = f'{message.author.mention} has taken too long to respond.'
            embed = discord.Embed(title= "Timeout Error", description=string, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            embed.set_footer(text="!removetask")
            await message.channel.send(file=file, embed=embed)
            return
        found = False
        for task in listTasks:
            if task[1] == removetask_action_content:
                found = True
                for deletetask in events:
                    if deletetask['summary'] == task[1]:
                        service.events().delete(calendarId='primary', eventId=deletetask['id']).execute()
                userDatabase.delete_task(str(message.author.id), removetask_action_content)

        if found:
            result_title = f'**Task Deleted**'
            result_description = f'{removetask_action_content} has been deleted/'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            embed.set_footer(text="!removetask")
            await message.channel.send(file=file, embed=embed)
        else:
            result_title = f'**Error**'
            result_description = f'{removetask_action_content} was not found. Please try again.'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            embed.set_footer(text="!removetask")
            await message.channel.send(file=file, embed=embed)
    else:
        result_title = f'Account Not Found'
        result_description = f'User not found for for **{message.author.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        embed.set_footer(text="!removetask")
        await message.channel.send(file=file, embed=embed)

async def completetask(message : discord.message.Message, client : discord.Client, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(message.author.id)):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)        

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    if os.path.exists("token.json"):
                        os.remove("token.json")
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port = 0)

                with open("token.json", "w") as token:
                    token.write(creds.to_json())
        service = build("calendar", "v3", credentials = creds)
        now = datetime.datetime.now().isoformat() + "Z"
        event_result = service.events().list(calendarId = "primary", timeMin=now, maxResults = 10, singleEvents = True, orderBy = "startTime").execute()
        events = event_result.get("items", [])
        data = userDatabase.get_tasks_by_id(str(message.author.id))
        if not events:
            print("No upcoming events found!")
        else:
            discord_id = str(message.author.id)    
            tasks_names = userDatabase.get_task_names_by_id(discord_id)
            for event in events:
                event_name = event['summary']
                event_start = event['start']['dateTime'][:19]
                event_end = event['end']['dateTime'][:19]       
                if event_name not in tasks_names:
                    userDatabase.add_task(str(message.author.id), event_name, event_start, event_end, False)
        data = userDatabase.get_tasks_by_id(str(message.author.id))
        def convert_to_datetime(date_str):
            try:
                return datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                print(f"Error: Invalid date string encountered: {date_str}")
                return None
        all_tasks = [task for task in data if task[4] == False]
        sorted_data = sorted(all_tasks, key=lambda x: convert_to_datetime(x[3]))
        result_title = f'**Name of the task you want to update**'
        result_description = f'**Please enter the name of the task**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        for i in sorted_data:
            string = f'{i[2]} to {i[3]}'
            embed.add_field(name=i[1], value=string, inline=False)
        embed.set_footer(text="!completetask")
        await message.channel.send(file=file, embed=embed)
        def check(m):
            return m.author == message.author and m.channel == message.channel
        removedtask_action = await client.wait_for('message', check=check, timeout=30)
        try:
            removetask_action_content = removedtask_action.content            
        except asyncio.TimeoutError:
            string = f'{message.author.mention} has taken too long to respond.'
            embed = discord.Embed(title= "Timeout Error", description=string, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            embed.set_footer(text="!completetask")
            await message.channel.send(file=file, embed=embed)
            return
        found = False
        for task in sorted_data:
            if task[1] == removetask_action_content:
                found = True
                for completetask in events:
                    if completetask['summary'] == task[1]:
                        service.events().delete(calendarId='primary', eventId=completetask['id']).execute()
                userDatabase.delete_task(str(message.author.id), removetask_action_content)

        if found:
            result_title = f'**Task Updated**'
            result_description = f'{removetask_action_content} has been updated/'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            embed.set_footer(text="!removetask")
            await message.channel.send(file=file, embed=embed)
        else:
            result_title = f'**Error**'
            result_description = f'{removetask_action_content} was not found. Please try again.'
            embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="HackPrinceton2024-Bot says:")
            embed.set_footer(text="!removetask")
            await message.channel.send(file=file, embed=embed)
    else:
        result_title = f'Account Not Found'
        result_description = f'User not found for for **{message.author.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="HackPrinceton2024-Bot says:")
        embed.set_footer(text="!completetask")
        await message.channel.send(file=file, embed=embed)