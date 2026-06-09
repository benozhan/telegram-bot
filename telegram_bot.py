import asyncio
import logging
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID   = 39206033
API_HASH = "06c5990bd3e612ca40f0b308b3b4e975"
SESSION  = os.environ.get("SESSION_STRING", "")
TARGET_CHANNEL = "@holiganozel"
SOURCE_CHANNEL = "holinormalcibot"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger(__name__)

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    text = event.message.raw_text
    if not text:
        return
    log.info(f"Yeni mesaj alındı")
    await client.send_message(TARGET_CHANNEL, text)
    log.info("Gönderildi.")

async def main():
    await client.start()
    log.info(f"{SOURCE_CHANNEL} dinleniyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
