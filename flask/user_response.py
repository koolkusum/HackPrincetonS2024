import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import random
import datetime

from user import User, UserDatabase

async def adduser(message : discord.message.Message, client : discord.Client, userDatabase : UserDatabase):
    if userDatabase.user_exists(str(message.author.id)):
        result_title = f'**User Already Created**'
        result_description = f'User already created for **{message.author.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="GreenHabits-Bot says:")
        embed.set_footer(text="!adduser")
        await message.channel.send(file=file, embed=embed)
    else:
        embed = discord.Embed(title = f'What time do you want GreenHabits-Bot to message you?', description='Please enter your prefered time in **military time format**.', color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="GreenHabits-Bot says:")
        embed.set_footer(text="!adduser")
        await message.channel.send(file=file, embed=embed)
        
        def check(m):
            return m.author == message.author and m.channel == message.channel
        prefered_time = await client.wait_for('message', check=check, timeout=30)
        try:
            def validate_time(time_str):
                hours, minutes = time_str.split(':')
                if not hours.isdigit() or not minutes.isdigit():
                    return False
                hours = int(hours)
                minutes = int(minutes)
                if hours < 0 or hours > 24 or minutes < 0 or minutes > 60:
                    return False
                return True
            prefered_time_content = prefered_time.content
            check = validate_time(prefered_time_content)
            if check:
                userDatabase.add_user(User(message.author.name, str(message.author.id), prefered_time_content))
                result_title = f'**User Created**'
                result_description = f'User created for **{message.author.mention}**'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('static/Images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="GreenHabits-Bot says:")
                embed.set_footer(text="!adduser")
                await message.channel.send(file=file, embed=embed)
            else:
                result_title = f'Invalid Output'
                result_description = f'Did not create user for **{message.author.mention}**'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('static/Images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="GreenHabits-Bot says:")
                embed.set_footer(text="!adduser")
                await message.channel.send(file=file, embed=embed)
        except asyncio.TimeoutError:
            # await message.channel.send(f'{message.author.mention} has taken too long to respond.')
            string = f'{message.author.mention} has taken too long to respond.'
            embed = discord.Embed(title= "Timeout Error", description=string, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="GreenHabits-Bot says:")
            embed.set_footer(text="!adduser")
            await message.channel.send(file=file, embed=embed)

async def userinfo(message : discord.message.Message, client : discord.Client, userDatabase : UserDatabase):
    if not userDatabase.user_exists(str(message.author.id)):
        result_title = f'**User Not Found**'
        result_description = f'User not found for **{message.author.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="GreenHabits-Bot says:")
        embed.set_footer(text="!userinfo")
        await message.channel.send(file=file, embed=embed)
    else:
        discord_id = str(message.author.id)
        info = userDatabase.get_user_by_id(discord_id)
        result_title = f'Information about {info[0]}'
        description_string = f'**Name:**\t\t{info[0]}\n**Discord ID:**\t{info[1]}\n**Preferred Time:**\t{info[2]}'
        embed = discord.Embed(title=result_title, description=description_string, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="GreenHabits-Bot says:")
        embed.set_footer(text="!userinfo")
        await message.channel.send(file=file, embed=embed)

async def changereminder(message : discord.message.Message, client : discord.Client, userDatabase : UserDatabase):
    if not userDatabase.user_exists(str(message.author.id)):
        result_title = f'User Not Found'
        result_description = f'User not found for **{message.author.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="GreenHabits-Bot says:")
        embed.set_footer(text="!changereminder")
        await message.channel.send(file=file, embed=embed)
    else:
        embed = discord.Embed(title = f'What time do you want to change it to?', description='Please enter in military time format:', color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="GreenHabits-Bot says:")      
        embed.set_footer(text="!changereminder")
        await message.channel.send(file=file, embed=embed)
        
        def check(m):
            return m.author == message.author and m.channel == message.channel
        reminder_action = await client.wait_for('message', check=check, timeout=30)
        try:
            reminder_action_content = reminder_action.content
            def validate_time(time_str):
                hours, minutes = time_str.split(':')
                if not hours.isdigit() or not minutes.isdigit():
                    return False
                hours = int(hours)
                minutes = int(minutes)
                if hours < 0 or hours > 24 or minutes < 0 or minutes > 60:
                    return False
                return True
            check = validate_time(reminder_action_content)
            if check:
                userDatabase.update_time_preference(str(message.author.id), reminder_action_content)
                result_title = f'Preference Time Changed'
                result_description = f'**{message.author.mention}** will be notified at {reminder_action_content}'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('static/Images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="GreenHabits-Bot says:")
                embed.set_footer(text="!changereminder")
                await message.channel.send(file=file, embed=embed)
            else:
                result_title = f'Invalid Output'
                result_description = f'Did not change preference time for **{message.author.mention}**'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('static/Images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="GreenHabits-Bot says:")
                embed.set_footer(text="!changereminder")
                await message.channel.send(file=file, embed=embed)
        except asyncio.TimeoutError:
            # await message.channel.send(f'{message.author.mention} has taken too long to respond.')
            string = f'{message.author.mention} has taken too long to respond.'
            embed = discord.Embed(title= "Timeout Error", description=string, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="GreenHabits-Bot says:")
            embed.set_footer(text="!changereminder")
            await message.channel.send(file=file, embed=embed)

async def deleteuser(message : discord.message.Message, client : discord.Client, userDatabase : UserDatabase):
    if not userDatabase.user_exists(str(message.author.id)):
        result_title = f'User Not Found'
        result_description = f'User not found for **{message.author.mention}**'
        embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="GreenHabits-Bot says:")
        embed.set_footer(text="!deleteuser")
        await message.channel.send(file=file, embed=embed)
    else:
        embed = discord.Embed(title = f'Are you sure?', description='Please return either:', color=0xFF5733)
        file = discord.File('static/Images/icon.png', filename='icon.png')
        embed.set_thumbnail(url='attachment://icon.png')
        embed.set_author(name="GreenHabits-Bot says:")
        embed.add_field(name="YES", value= "to confirm the delete action")
        embed.add_field(name="NO", value= "to exit the delete action")        
        embed.set_footer(text="!adduser")
        await message.channel.send(file=file, embed=embed)
        
        def check(m):
            return m.author == message.author and m.channel == message.channel
        exit_action = await client.wait_for('message', check=check, timeout=30)
        try:
            exit_action_content = exit_action.content
            if exit_action_content.upper() == 'YES':
                userDatabase.delete_user(str(message.author.id))
                result_title = f'**User Deleted**'
                result_description = f'User deleted for **{message.author.mention}**'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('static/Images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="GreenHabits-Bot says:")
                embed.set_footer(text="!adduser")
                await message.channel.send(file=file, embed=embed)
            elif exit_action_content.upper() == 'NO':
                result_title = f'**Exit Terminated**'
                result_description = f'Did not delete for **{message.author.mention}**'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('static/Images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="GreenHabits-Bot says:")
                embed.set_footer(text="!adduser")
                await message.channel.send(file=file, embed=embed)
            else:
                result_title = f'**Invalid Input**'
                result_description = f'Did not delete for **{message.author.mention}**'
                embed = discord.Embed(title=result_title, description=result_description, color=0xFF5733)
                file = discord.File('static/Images/icon.png', filename='icon.png')
                embed.set_thumbnail(url='attachment://icon.png')
                embed.set_author(name="GreenHabits-Bot says:")
                embed.set_footer(text="!adduser")
                await message.channel.send(file=file, embed=embed)
        except asyncio.TimeoutError:
            # await message.channel.send(f'{message.author.mention} has taken too long to respond.')
            string = f'{message.author.mention} has taken too long to respond.'
            embed = discord.Embed(title= "Timeout Error", description=string, color=0xFF5733)
            file = discord.File('static/Images/icon.png', filename='icon.png')
            embed.set_thumbnail(url='attachment://icon.png')
            embed.set_author(name="GreenHabits-Bot says:")
            embed.set_footer(text="!deleteuser")
            await message.channel.send(file=file, embed=embed)