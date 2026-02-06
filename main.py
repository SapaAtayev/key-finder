import os
import sys
import asyncio
import uuid
import logging
from datetime import datetime, timedelta

import aiofiles
from telethon import TelegramClient, events, functions, types
from dotenv import load_dotenv

# Import our extraction module
import extract_configs

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load Environment Variables
load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = os.getenv('TELEGRAM_SESSION_NAME', 'key_finder_session')
FORWARD_CHANNEL_ID = os.getenv('FORWARD_CHANNEL_ID')
MONITOR_USER_LIST = os.getenv('MONITOR_USER_LIST', '')

# Validation
if not API_ID or not API_HASH:
    logger.error("TELEGRAM_API_ID or TELEGRAM_API_HASH not found in .env file.")
    sys.exit(1)

try:
    API_ID = int(API_ID)
    if FORWARD_CHANNEL_ID:
        FORWARD_CHANNEL_ID = int(FORWARD_CHANNEL_ID)
except ValueError:
    logger.error("API_ID and FORWARD_CHANNEL_ID must be integers.")
    sys.exit(1)

# Initialize Client
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def get_groups():
    """
    Fetches groups from a specific folder named 'Network' or all dialogs if not found.
    Refactored to be more robust.
    """
    groups = []
    try:
        dialogs = await client.get_dialogs()
        # Logic to filter by folder "Network" if strictly required, 
        # but for now let's use the explicit user list from env + 'Network' folder if it exists.
        
        req = await client(functions.messages.GetDialogFiltersRequest())
        for x in req.filters:
            if hasattr(x, 'title') and x.title and x.title.text == "Network":
                for peer in x.include_peers:
                    try:
                        entity = await client.get_entity(peer)
                        groups.append(entity)
                    except Exception as e:
                        logger.warning(f"Could not get entity for peer {peer}: {e}")
    except Exception as e:
        logger.error(f"Error fetching dialog filters: {e}")

    return groups

async def extract_code_string(message):
    search_text = ["darktunnel://", "dns-query", "proxy", "ss://", "vless://", "happ://", "/sub/", "vmess://", "trojan", "hysteria"]
    msg_content = message.message.lower()
    
    for x in search_text:
        if x in msg_content:
            logger.info(f"Found keyword: {x}")
            
            # Forward if channel ID is configured
            if FORWARD_CHANNEL_ID:
                try:
                    await client.forward_messages(FORWARD_CHANNEL_ID, message)
                except Exception as e:
                    logger.error(f"Failed to forward message: {e}")

            # Save to file
            async with aiofiles.open("extracted_codes.txt", mode="a", encoding="utf-8") as f:
                await f.write(message.message + "\n\n")
            break

async def handler():
    groups = await get_groups()
    logger.info(f"Found {len(groups)} entities in 'Network' folder.")

    # Process explicit user list from .env
    user_list_items = [u.strip() for u in MONITOR_USER_LIST.split(',') if u.strip()]
    for user_entry in user_list_items:
        try:
            entity = await client.get_entity(user_entry)
            if entity and entity not in groups: # Avoid duplicates if possible, though Entity objects might not compare equal directly
                groups.append(entity)
        except Exception as e:
            logger.warning(f"Could not resolve explicit user/group '{user_entry}': {e}")

    # Clean up extracted_codes.txt before starting
    if os.path.exists("extracted_codes.txt"):
        os.remove("extracted_codes.txt")

    for group_entity in groups:
        group_name = getattr(group_entity, 'title', getattr(group_entity, 'first_name', str(group_entity.id)))
        logger.info(f"Scanning entity: '{group_name}' ({group_entity.id})")

        try:
            # Iterating through messages
            async for message in client.iter_messages(group_entity, limit=20):
                if not message.date:
                    continue
                
                # Check if message is within the last 24 hours
                if (datetime.now(message.date.tzinfo) - message.date) <= timedelta(days=1):
                    if message.message:
                        await extract_code_string(message)
        except Exception as e:
            logger.error(f"Error processing '{group_name}': {e}")

def main():
    logger.info("Starting Telegram Key Finder...")
    
    with client:
        client.loop.run_until_complete(handler())
    
    logger.info("Telegram scan complete. Starting config extraction and upload...")
    
    # Run the extraction and upload process
    secrets_file = os.getenv('GOOGLE_CLIENT_SECRETS_FILE', 'client_secrets.json')
    folder_ids = os.getenv('GDRIVE_FOLDER_IDS', '').split(',')
    folder_ids = [f.strip() for f in folder_ids if f.strip()]
    
    extract_configs.run_extraction(source_file='extracted_codes.txt', client_secrets=secrets_file, folder_ids=folder_ids)

if __name__ == '__main__':
    main()
