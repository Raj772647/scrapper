import os
from pyrogram import Client, filters
from pyrogram.types import Message
import re
import pymongo
import requests
import json
from collections import Counter
import traceback

# MongoDB connection
client = pymongo.MongoClient(
    "mongodb+srv://rajveer6053:Raj7726821605@cluster0.ktunb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

db = client.credit_cards

# API credentials
api_id = os.environ.get('api_id') or "23181335"
api_hash = os.environ.get('api_hash') or "b73ae83eab9abcc69449039344b0e73a"
bot_token = os.environ.get('bot_token') or "7798211459:AAGxzwQVjGyXyEmLeinfskzOAqIAg8t-X7A"

# Telegram identifiers
chat_id = "-1002354281978"  # Your chat ID
admins = ["6389955589"]  # Your Telegram ID as admin

# Bot and App Clients
bot = Client(
    "My_Project",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

app = Client(
    name="me",
    api_id=api_id,
    api_hash=api_hash
)

# Start Command
@bot.on_message(filters.command('start') & filters.private)
def command1(bot, message):
    bot.send_message(message.chat.id, "Heya, I am a simple test bot.")

# Help Command
@bot.on_message(filters.command('help'))
def command2(bot, message):
    message.reply_text("HELP IS ON THE WAY")

# Welcome New Members
@bot.on_message(filters.chat(chat_id) & filters.new_chat_members)
def welcomebot(client, message):
    message.reply_text("Welcome")

# Add Admin Command
@bot.on_message(filters.command('add_admin') & filters.private)
def add_admin(client, message):
    global admins
    if str(message.from_user.id) in admins:  # Check if sender is already an admin
        try:
            new_admin_id = message.text.split(" ")[1]
            if new_admin_id not in admins:
                admins.append(new_admin_id)
                client.send_message(chat_id=message.chat.id, text=f"Admin {new_admin_id} added successfully!")
            else:
                client.send_message(chat_id=message.chat.id, text="User is already an admin.")
        except IndexError:
            client.send_message(chat_id=message.chat.id, text="Please provide a valid user ID.")
    else:
        client.send_message(chat_id=message.chat.id, text="You are not authorized to add admins.")

# Join Chat Command
@bot.on_message(filters.command('join') & filters.private)
async def joinchat(client, message):
    try:
        # Extract chat link or username from the command
        command_args = message.text.split(" ", 1)
        if len(command_args) < 2:
            await message.reply_text("Usage: /join <chat_link_or_username>")
            return

        chat_identifier = command_args[1]

        # Attempt to join the chat
        try:
            await app.join_chat(chat_identifier)
            await message.reply_text(f"Successfully joined {chat_identifier}!")
        except Exception as e:
            # Retry by converting the link to a username format
            if "https://t.me/" in chat_identifier:
                chat_identifier = chat_identifier.split("https://t.me/")[-1]
                await app.join_chat(chat_identifier)
                await message.reply_text(f"Successfully joined {chat_identifier}!")
            else:
                raise e
    except Exception as e:
        error_message = f"An error occurred while trying to join: {str(e)}"
        await message.reply_text(error_message)

# Max BIN Command
@bot.on_message(filters.command("max"))
async def maxbin(Client, message):
    global bins
    bins_count_text = []
    mess = eval(str(message))
    userr = mess["chat"]["id"]
    if userr in admins:
        c = Counter(bins)
        p = (c.most_common(20))
        for i in range(len(p)):
            binn = p[i][0]
            ctr = p[i][1]
            z = "<b>Top-</b>{} : <b>Bin -</b><code>{}</code> : <b>Count - </b><code>{}</code>".format(i + 1, binn, ctr)
            bins_count_text.append(z)
        test_text = "\n".join(bins_count_text)
        await bot.send_message(chat_id=userr, text=test_text)
    else:
        text = "Not Authorized!"
        await bot.send_message(chat_id=userr, text=text)

# Scrape Command
@bot.on_message(filters.command("scrape"))
async def scrape(Client, message):
    global bins
    try:
        command_args = message.text.split(" ")
        if len(command_args) < 3:
            await message.reply_text("Usage: /scrape <BIN> <count> <channel_username>")
            return

        binz = command_args[1]
        t_count = int(command_args[2])
        cha = command_args[3] if len(command_args) > 3 else "default_channel"

        file_path = f"{binz}_{cha}.txt"
        count = 0

        async for i in app.get_chat_history(cha):
            if count >= t_count:
                break

            if i.text:
                try:
                    ter = str(i.text)
                    te = re.sub('[^0-9|/]', '', ter)
                    t = re.sub(' +', ' ', te)
                    rawdata = t

                    filtro = "[0-9]{16}[|][0-9]{1,2}[|][0-9]{2,4}[|][0-9]{3}"
                    matches = re.findall(filtro, rawdata)

                    for match in matches:
                        if binz in match[:8]:
                            with open(file_path, "a") as file:
                                file.write(match + "\n")
                            count += 1
                except Exception as e:
                    print(f"Error processing message: {e}")

        if count > 0:
            await bot.send_document(chat_id=message.chat.id, document=file_path)
            os.remove(file_path)
        else:
            await message.reply_text("No matching data found.")

    except Exception as e:
        error_message = f"An error occurred during scraping: {str(e)}\n{traceback.format_exc()}"
        await message.reply_text(error_message)

# Start the bot
print("Successfully Deployed Bot")
bot.start()
app.run()