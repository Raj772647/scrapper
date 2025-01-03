import os
from pyrogram import Client, filters
from pyrogram.types import Message
import re
import pymongo
import requests
import json
from collections import Counter

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

# Join Chat Command
@bot.on_message(filters.command('join') & filters.private)
async def joinchat(Client, message):
    global linked
    mess = eval(str(message))
    tet = (mess["text"]).split(" ", 1)
    userr = mess["from_user"]["id"]
    try:
        try:
            await app.join_chat(tet[-1])
            text = "Joined Successfully!"
            await bot.send_message(chat_id=userr, text=text)
        except Exception as e:
            tt = tet[-1].split("https://t.me/")
            linkk = "@{}".format(tt[-1])
            await app.join_chat(linkk)
            text = "Joined Successfully!"
            await bot.send_message(chat_id=userr, text=text)
    except Exception as e:
        text = "The user is already a participant of this chat"
        await bot.send_message(chat_id=userr, text=text)

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
    ctr = 0
    count = 0
    mess = eval(str(message))
    userr = mess["chat"]["id"]
    if userr in admins:
        a_m = await bot.send_message(chat_id=message.chat.id, text="𝑳𝒐𝒂𝒅𝒊𝒏𝒈 ⬡⬡⬡")
        try:
            tet = (mess["text"]).split(" ", 3)
            cha = tet[3]
            t_count = int(tet[-2])
            binz = str(tet[1])
        except:
            tet = (mess["text"]).split(" ", 2)
            cha = "asurccworld_scrapper"
            t_count = int(tet[2])
            binz = str(tet[1])
        print(cha, t_count, binz)
        file = open(f"{binz}_{cha}.txt", "w")
        a_m = await bot.edit_message_text(chat_id=message.chat.id, message_id=a_m.id, text="𝑳𝒐𝒂𝒅𝒊𝒏𝒈 ⬣⬡⬡")

        async for i in app.get_chat_history(cha):
            ctr += 1
            if not i.text:
                continue
            try:
                ter = str(i.text)
                te = re.sub('[^0-9|/]', '', ter)
                t = re.sub(' +', ' ', te)
                rawdata = (t)

                detectavisa = "[0-9]{16}"
                filtro = "[0-9]{16}[|][0-9]{1,2}[|][0-9]{2,4}[|][0-9]{3}"
                x = re.findall(filtro, rawdata)[0]
                x = x.replace(" ", "|").replace("/", "|")

                if binz in x[:8]:
                    file.write(x + "\n")
                    count += 1
            except:
                pass

        file.close()
        await bot.send_document(chat_id=message.chat.id, document=f"{binz}_{cha}.txt")
        os.remove(f"{binz}_{cha}.txt")
    else:
        text = "Not Authorized!"
        await bot.send_message(chat_id=userr, text=text)

# Start the bot
print("Successfully Deployed Bot")
bot.start()
app.run()
