import os
from pyrogram import Client, filters
import re
import traceback
import json

# API credentials
api_id = os.environ.get('api_id') or "23181335"
api_hash = os.environ.get('api_hash') or "b73ae83eab9abcc69449039344b0e73a"
bot_token = os.environ.get('bot_token') or "7798211459:AAGxzwQVjGyXyEmLeinfskzOAqIAg8t-X7A"

# File to store source channels
SOURCE_CHANNELS_FILE = "source_channels.json"

# Target channel ID
target_channel_id = -1002354281978  # Replace with your target channel's chat ID

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

# Load source channels from file
def load_source_channels():
    if os.path.exists(SOURCE_CHANNELS_FILE):
        with open(SOURCE_CHANNELS_FILE, "r") as f:
            return json.load(f)
    return {}

# Save source channels to file
def save_source_channels(channels):
    with open(SOURCE_CHANNELS_FILE, "w") as f:
        json.dump(channels, f)

# Initialize source channels
source_channels = load_source_channels()

# Function to fetch and process messages from a single source channel
async def fetch_messages(username, config):
    try:
        print(f"Fetching messages from {username}...")
        chat = await app.get_chat(username)  # Resolve username to chat ID
        chat_id = chat.id

        count = 0

        # Fetch all messages from the channel
        async for message in app.get_chat_history(chat_id):
            if message.text:
                # Filter the message content
                rawdata = re.sub(r"[^0-9|/]", "", message.text)
                rawdata = re.sub(r" +", " ", rawdata)

                # Apply channel-specific regex filter
                matches = re.findall(config["filter"], rawdata)

                if matches:
                    # Customize and forward the message
                    forwarded_message = f"Source: {config['name']}\n\n{message.text}"
                    await app.send_message(chat_id=target_channel_id, text=forwarded_message)
                    count += 1

        print(f"Processed {count} messages from {config['name']} ({username}).")
        return count

    except Exception as e:
        print(f"Error processing channel {config['name']} ({username}): {e}")
        return 0


# Command to add a new source channel
@bot.on_message(filters.command("add_channel"))
async def add_channel(Client, message):
    try:
        parts = message.text.split(" ", 3)
        if len(parts) < 4:
            await message.reply_text("Usage: /add_channel <username> <name> <regex_filter>")
            return

        username, name, regex_filter = parts[1], parts[2], parts[3]

        if username in source_channels:
            await message.reply_text(f"Channel {username} already exists.")
            return

        source_channels[username] = {"name": name, "filter": regex_filter}
        save_source_channels(source_channels)

        await message.reply_text(f"Added new channel: {name} ({username}) with filter: {regex_filter}")

    except Exception as e:
        await message.reply_text(f"An error occurred while adding the channel: {e}")


# Scrape and process messages from all configured channels
@bot.on_message(filters.command("scrape"))
async def scrape(Client, message):
    try:
        total_count = 0

        for username, config in source_channels.items():
            count = await fetch_messages(username, config)
            total_count += count

        await message.reply_text(
            f"Processed and forwarded {total_count} messages." if total_count else "No messages were processed."
        )

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}\n{traceback.format_exc()}")


# Start the bot
print("Successfully Deployed Bot")
bot.start()
app.run()
