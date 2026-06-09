"""
Holigan Odds Forwarder
----------------------
holinormalcibot kanalını dinler, mesajları kendi kanalına iletir.
"""

import asyncio
import logging
from telethon import TelegramClient, events

# ─── AYARLAR ───────────────────────────
API_ID   = 39206033              # my.telegram.org/apps'ten al
API_HASH = "06c5990bd3e612ca40f0b308b3b4e975"             # my.telegram.org/apps'ten al
PHONE    = "+905453663321"             # +905xxxxxxxxx

SOURCE_CHANNEL = "holinormalcibot"   # dinlenecek kanal
TARGET_CHANNEL = "@holiganozel"                  # senin kanalın (@kanal_adi)
# ────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s"
)
log = logging.getLogger(__name__)

client = TelegramClient("session", API_ID, API_HASH)

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    text = event.message.raw_text
    if not text:
        return
    log.info(f"Yeni mesaj alındı ({len(text)} karakter)")
    await client.send_message(TARGET_CHANNEL, text)
    log.info("Gönderildi.")

async def main():
    await client.start(phone=PHONE)
    log.info(f"{SOURCE_CHANNEL} dinleniyor...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
