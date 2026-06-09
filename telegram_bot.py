"""
Holigan Özel Oran Bot - WebSocket versiyonu
"""

import asyncio
import json
import logging
import hashlib
import os
from datetime import datetime
from telethon import TelegramClient
from telethon.sessions import StringSession
import websockets

API_ID   = 39206033
API_HASH = "06c5990bd3e612ca40f0b308b3b4e975"
SESSION  = os.environ.get("SESSION_STRING", "")
TARGET_CHANNEL = "@holiganozel"

WS_URL = "wss://sportsapi.holiganbet7602.com/v2"
HEADERS = {
    "Origin": "https://sports2.holiganbet7602.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(message)s")
log = logging.getLogger(__name__)
seen = set()

def make_id(data):
    return hashlib.md5(data.encode()).hexdigest()[:12]

def format_coupon(events):
    if not events:
        return ""
    total = 1.0
    lines = ["🎰 *HOLİGAN ÖZEL ORAN*", "_Holigan site oranları analizi_", "", "✅ *Kupon Analizi*", ""]
    for ev in events:
        odds = ev.get("odds", 0.0)
        if odds > 0:
            total *= odds
        lines.append(f"⚽ {ev.get('home','')} - {ev.get('away','')}")
        lines.append(f"📈 *{ev.get('prediction','—')}:* `{odds:.2f}`")
        if ev.get("league"):
            lines.append(f"🏆 {ev['league']}")
        if ev.get("date"):
            lines.append(f"📅 {ev['date']}")
        lines.append("")
    lines += ["────────────────────", f"🎯 *Toplam Kupon Oranı:* `{total:.2f}`"]
    return "\n".join(lines)

def parse_boosted_events(payload):
    events = []
    records = payload.get("records", [])
    current_event = {}
    for rec in records:
        entity = rec.get("entityType", "")
        d = rec.get("data", {})
        if entity == "EVENT":
            start = d.get("start", "")
            try:
                date_str = datetime.fromtimestamp(int(start)/1000).strftime("%a, %d %B %H:%M") if start else ""
            except:
                date_str = ""
            current_event = {
                "home": d.get("homeName", ""),
                "away": d.get("awayName", ""),
                "league": d.get("tournamentName", ""),
                "date": date_str,
            }
        elif entity == "OUTCOME" and current_event:
            odds = d.get("odds", 0)
            boosted = d.get("boostedOdds", 0)
            actual = boosted if boosted and boosted > odds else odds
            if actual > 1.0:
                ev = dict(current_event)
                ev["prediction"] = d.get("label", d.get("name", "—"))
                ev["odds"] = round(actual / 1000 if actual > 100 else actual, 2)
                events.append(ev)
                current_event = {}
    return events

async def holigan_ws(tg):
    req_id = 1
    while True:
        try:
            log.info(f"Bağlanıyor: {WS_URL}")
            async with websockets.connect(
                WS_URL,
                additional_headers=HEADERS,
                subprotocols=["wamp.2.json"],
                ping_interval=30,
            ) as ws:
                log.info("Bağlandı!")
                await ws.send(json.dumps([1, "www.holiganbet.com", {"agent": "Wampy.js v6.2.2", "roles": {"publisher": {"features": {}}}}]))
                await asyncio.sleep(1)
                for topic in [
                    "sports/2218/tr/locations/101/NOT_LIVE/BOTH",
                    "sports/2218/tr/disciplines/BOTH/BOTH",
                    "sports/2218/tr/tournaments/101/240",
                    "sports/2218/tr/tournaments-by-event-category/0",
                    "sports/2218/tr/custom-sports",
                    "sports/2218/tr/custom-events",
                ]:
                    req_id += 1
                    await ws.send(json.dumps([64, req_id, {}, topic]))
                    await asyncio.sleep(0.2)
                log.info("Özel oranlar dinleniyor...")
                async for raw in ws:
                    try:
                        msg = json.loads(raw)
                        if not isinstance(msg, list) or len(msg) < 6 or msg[0] != 68:
                            continue
                        payload = msg[5] if len(msg) > 5 else {}
                        if not isinstance(payload, dict):
                            continue
                        if payload.get("messageType") not in ("UPDATE", "FULL_STATE"):
                            continue
                        records = payload.get("records", [])
                        has_boost = any(
                            rec.get("data", {}).get("boostedOdds")
                            for rec in records if rec.get("entityType") == "OUTCOME"
                        )
                        if not has_boost:
                            continue
                        events = parse_boosted_events(payload)
                        if not events:
                            continue
                        cid = make_id(json.dumps(events, sort_keys=True))
                        if cid in seen:
                            continue
                        seen.add(cid)
                        text = format_coupon(events)
                        if text:
                            log.info(f"Yeni kupon! {len(events)} maç")
                            await tg.send_message(TARGET_CHANNEL, text, parse_mode="markdown")
                            log.info("Gönderildi.")
                    except Exception as e:
                        log.debug(f"Parse hatası: {e}")
        except Exception as e:
            log.error(f"WS hatası: {e} — 10sn sonra yeniden...")
            await asyncio.sleep(10)

async def main():
    log.info("Bot başlatılıyor...")
    tg = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
    await tg.start()
    log.info("Telegram bağlı.")
    await holigan_ws(tg)

if __name__ == "__main__":
    asyncio.run(main())
