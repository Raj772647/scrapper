import os
from pyrogram import Client, filters
from pyrogram.errors import ChannelInvalid, PeerIdInvalid
from pyrogram.types import Message
import re
import pymongo
import requests
import json
from collections import Counter
import traceback
import logging

# Enable logging for card detection
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
#mene changes krk dekhe
# Enhanced Card pattern regex
CARD_PATTERN = r'(?:\d{16}|\d{4}[- ]\d{4}[- ]\d{4}[- ]\d{4}|\d{4}\s\d{4}\s\d{4}\s\d{4})'

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
source_channels = [-1002400544051]
target_channels = [-1002354281978]

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

# Admin Control Command
@bot.on_message(filters.command('admin') & filters.private)
async def admin_control(client, message):
    global admins, source_channels, target_channels
    if str(message.from_user.id) in admins:
        try:
            command_args = message.text.split(" ", 2)
            if len(command_args) < 2:
                await message.reply_text("Usage: /admin <add_admin|add_source|add_target|join> <value>")
                return
            
            action = command_args[1]
            value = command_args[2] if len(command_args) > 2 else None
            
            if action == 'add_admin' and value:
                if value not in admins:
                    admins.append(value)
                    await message.reply_text(f"Admin {value} added successfully!")
                else:
                    await message.reply_text("User is already an admin.")
            
            elif action == 'add_source' and value:
                if value not in source_channels:
                    source_channels.append(value)
                    await message.reply_text(f"Source channel {value} added successfully!")
                else:
                    await message.reply_text("Channel is already in source list.")
            
            elif action == 'add_target' and value:
                if value not in target_channels:
                    target_channels.append(value)
                    await message.reply_text(f"Target channel {value} added successfully!")
                else:
                    await message.reply_text("Channel is already in target list.")
            
            elif action == 'join' and value:
                try:
                    await app.join_chat(value)
                    await message.reply_text(f"Successfully joined {value}!")
                except (ChannelInvalid, PeerIdInvalid) as e:
                    await message.reply_text(f"Failed to join: {str(e)}")
            else:
                await message.reply_text("Invalid action or missing value.")
        except IndexError:
            await message.reply_text("Invalid usage. Use: /admin <add_admin|add_source|add_target|join> <value>")
    else:
        await message.reply_text("You are not authorized to perform admin actions.")

# Forward Messages from Source to Target (Real-Time)
@app.on_message(filters.chat(source_channels))
async def forward_messages(client, message):
    try:
        # Log incoming message
        logger.info(f"Received message from channel {message.chat.id}")
        
        # Get message text from different types of messages
        message_text = ""
        if message.text:
            message_text = message.text
        elif message.caption:
            message_text = message.caption
            
        logger.info(f"Processing message: {message_text[:100]}...")  # Log first 100 chars
        
        # Check for card numbers in message
        card_numbers = re.findall(CARD_PATTERN, message_text)
        
        if card_numbers:
            logger.info(f"💳 Found {len(card_numbers)} card numbers")
            logger.info(f"💳 Cards: {card_numbers}")
            
            # Forward to all target channels
            for target in target_channels:
                try:
                    logger.info(f"Attempting to forward to target {target}")
                    
                    if message.text:
                        sent_msg = await client.send_message(
                            chat_id=target,
                            text=message_text
                        )
                        logger.info("✅ Forwarded text message successfully")
                    
                    elif message.photo:
                        sent_msg = await client.send_photo(
                            chat_id=target,
                            photo=message.photo.file_id,
                            caption=message.caption
                        )
                        logger.info("✅ Forwarded photo message successfully")
                    
                    elif message.video:
                        sent_msg = await client.send_video(
                            chat_id=target,
                            video=message.video.file_id,
                            caption=message.caption
                        )
                        logger.info("✅ Forwarded video message successfully")
                    
                    elif message.document:
                        sent_msg = await client.send_document(
                            chat_id=target,
                            document=message.document.file_id,
                            caption=message.caption
                        )
                        logger.info("✅ Forwarded document message successfully")
                    
                    else:
                        sent_msg = await message.copy(chat_id=target)
                        logger.info("✅ Forwarded message using copy method")
                    
                    # Store in MongoDB
                    try:
                        card_data = {
                            "card_numbers": card_numbers,
                            "full_message": message_text,
                            "timestamp": message.date,
                            "source_channel": str(message.chat.id),
                            "target_channel": str(target),
                            "message_type": "text" if message.text else "media"
                        }
                        db.cards.insert_one(card_data)
                        logger.info("💾 Stored card data in MongoDB")
                    except Exception as db_error:
                        logger.error(f"❌ MongoDB Error: {str(db_error)}")
                    
                except Exception as e:
                    logger.error(f"❌ Forward Error: {str(e)}")
                    traceback.print_exc()
        else:
            logger.info("No card numbers found in this message")
            
    except Exception as e:
        logger.error(f"❌ Main Error: {str(e)}")
        traceback.print_exc()

# Start the bot
print("Successfully Deployed Bot")
bot.start()
app.run()
