import json
import os
import re
import hashlib
import unicodedata
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

BOT_TOKEN = "8821012001:AAGLE8O3SkY-1_vIKiDDiu23dLLUdGbz0ac"
ODDS_API_KEY = "b8c77d4166c9bb4d23bd0e14b4904e83"

CACHE_FILE = "odds_cache.json"
BOLGE = "eu"

kullanici_kuponlari = {}

ULKE_CEVIRI = {
    "Afghanistan": "Afganistan", "Albania": "Arnavutluk", "Algeria": "Cezayir",
    "Andorra": "Andorra", "Angola": "Angola", "Argentina": "Arjantin",
    "Armenia": "Ermenistan", "Australia": "Avustralya", "Austria": "Avusturya",
    "Azerbaijan": "Azerbaycan", "Bahamas": "Bahamalar", "Bahrain": "Bahreyn",
    "Bangladesh": "Bangladeş", "Belarus": "Belarus", "Belgium": "Belçika",
    "Belize": "Belize", "Benin": "Benin", "Bhutan": "Butan", "Bolivia": "Bolivya",
    "Bosnia and Herzegovina": "Bosna Hersek", "Botswana": "Botsvana",
    "Brazil": "Brezilya", "Bulgaria": "Bulgaristan", "Burkina Faso": "Burkina Faso",
    "Burundi": "Burundi", "Cambodia": "Kamboçya", "Cameroon": "Kamerun",
    "Canada": "Kanada", "Cape Verde": "Yeşil Burun Adaları",
    "Central African Republic": "Orta Afrika Cumhuriyeti", "Chad": "Çad",
    "Chile": "Şili", "China": "Çin", "Colombia": "Kolombiya",
    "Comoros": "Komorlar", "Congo": "Kongo", "Costa Rica": "Kosta Rika",
    "Croatia": "Hırvatistan", "Cuba": "Küba", "Cyprus": "Kıbrıs",
    "Czech Republic": "Çekya", "Czechia": "Çekya", "Denmark": "Danimarka",
    "Djibouti": "Cibuti", "Dominican Republic": "Dominik Cumhuriyeti",
    "Ecuador": "Ekvador", "Egypt": "Mısır", "El Salvador": "El Salvador",
    "England": "İngiltere", "Equatorial Guinea": "Ekvator Ginesi",
    "Eritrea": "Eritre", "Estonia": "Estonya", "Ethiopia": "Etiyopya",
    "Finland": "Finlandiya", "France": "Fransa", "Gabon": "Gabon",
    "Gambia": "Gambiya", "Georgia": "Gürcistan", "Germany": "Almanya",
    "Ghana": "Gana", "Greece": "Yunanistan", "Guatemala": "Guatemala",
    "Guinea": "Gine", "Haiti": "Haiti", "Honduras": "Honduras",
    "Hungary": "Macaristan", "Iceland": "İzlanda", "India": "Hindistan",
    "Indonesia": "Endonezya", "Iran": "İran", "Iraq": "Irak",
    "Ireland": "İrlanda", "Israel": "İsrail", "Italy": "İtalya",
    "Ivory Coast": "Fildişi Sahili", "Cote d'Ivoire": "Fildişi Sahili",
    "Jamaica": "Jamaika", "Japan": "Japonya", "Jordan": "Ürdün",
    "Kazakhstan": "Kazakistan", "Kenya": "Kenya", "Kosovo": "Kosova",
    "Kuwait": "Kuveyt", "Kyrgyzstan": "Kırgızistan", "Latvia": "Letonya",
    "Lebanon": "Lübnan", "Liberia": "Liberya", "Libya": "Libya",
    "Lithuania": "Litvanya", "Luxembourg": "Lüksemburg",
    "Madagascar": "Madagaskar", "Malaysia": "Malezya", "Maldives": "Maldivler",
    "Mali": "Mali", "Malta": "Malta", "Mexico": "Meksika",
    "Moldova": "Moldova", "Monaco": "Monako", "Mongolia": "Moğolistan",
    "Montenegro": "Karadağ", "Morocco": "Fas", "Mozambique": "Mozambik",
    "Netherlands": "Hollanda", "New Zealand": "Yeni Zelanda",
    "Nicaragua": "Nikaragua", "Nigeria": "Nijerya", "North Macedonia": "Kuzey Makedonya",
    "Northern Ireland": "Kuzey İrlanda", "Norway": "Norveç", "Oman": "Umman",
    "Pakistan": "Pakistan", "Palestine": "Filistin", "Panama": "Panama",
    "Paraguay": "Paraguay", "Peru": "Peru", "Philippines": "Filipinler",
    "Poland": "Polonya", "Portugal": "Portekiz", "Qatar": "Katar",
    "Romania": "Romanya", "Russia": "Rusya", "Rwanda": "Ruanda",
    "San Marino": "San Marino", "Saudi Arabia": "Suudi Arabistan",
    "Scotland": "İskoçya", "Senegal": "Senegal", "Serbia": "Sırbistan",
    "Slovakia": "Slovakya", "Slovenia": "Slovenya", "South Africa": "Güney Afrika",
    "South Korea": "Güney Kore", "Korea Republic": "Güney Kore",
    "Spain": "İspanya", "Sri Lanka": "Sri Lanka", "Sudan": "Sudan",
    "Sweden": "İsveç", "Switzerland": "İsviçre", "Syria": "Suriye",
    "Thailand": "Tayland", "Tunisia": "Tunus", "Turkey": "Türkiye",
    "Turkiye": "Türkiye", "Ukraine": "Ukrayna", "United Arab Emirates": "BAE",
    "UAE": "BAE", "United States": "ABD", "USA": "ABD", "Uruguay": "Uruguay",
    "Uzbekistan": "Özbekistan", "Venezuela": "Venezuela", "Vietnam": "Vietnam",
    "Wales": "Galler", "Zambia": "Zambiya", "Zimbabwe": "Zimbabve",
}

TAKIM_CEVIRI = {
    "Manchester United": "Manchester United",
    "Manchester City": "Manchester City",
    "Real Madrid": "Real Madrid",
    "Barcelona": "Barcelona",
    "Bayern Munich": "Bayern Münih",
    "Borussia Dortmund": "Borussia Dortmund",
    "Galatasaray": "Galatasaray",
    "Fenerbahce": "Fenerbahçe",
    "Fenerbahçe": "Fenerbahçe",
    "Besiktas": "Beşiktaş",
    "Beşiktaş": "Beşiktaş",
    "Trabzonspor": "Trabzonspor",
    "Inter Milan": "Inter",
    "AC Milan": "Milan",
    "Juventus": "Juventus",
    "Paris Saint Germain": "PSG",
    "Paris Saint-Germain": "PSG",
}

ARANACAK_CEVIRI = {
    "kanada": "canada", "arjantin": "argentina", "sili": "chile", "şili": "chile",
    "brezilya": "brazil", "almanya": "germany", "ispanya": "spain",
    "fransa": "france", "ingiltere": "england", "italya": "italy",
    "hollanda": "netherlands", "turkiye": "turkey", "türkiye": "turkey",
    "abd": "usa", "fildisi": "ivory", "fildişi": "ivory",
    "kadin": "women", "kadın": "women", "bayern munih": "bayern munich",
    "fenerbahce": "fenerbahce", "besiktas": "besiktas",
}


def temiz_yazi(yazi):
    yazi = str(yazi).lower().strip()
    yazi = unicodedata.normalize("NFKD", yazi)
    yazi = "".join(c for c in yazi if not unicodedata.combining(c))

    for tr, en in ARANACAK_CEVIRI.items():
        tr_norm = unicodedata.normalize("NFKD", tr)
        tr_norm = "".join(c for c in tr_norm if not unicodedata.combining(c))
        yazi = yazi.replace(tr_norm, en)

    yazi = re.sub(r"[^a-z0-9 ]", " ", yazi)
    return re.sub(r"\s+", " ", yazi).strip()


def turkce_ad(ad):
    sonuc = str(ad)

    for ing, tr in sorted(TAKIM_CEVIRI.items(), key=lambda x: len(x[0]), reverse=True):
        sonuc = sonuc.replace(ing, tr)

    for ing, tr in sorted(ULKE_CEVIRI.items(), key=lambda x: len(x[0]), reverse=True):
        sonuc = sonuc.replace(ing, tr)

    sonuc = sonuc.replace("Women", "Kadın")
    sonuc = sonuc.replace("W", "Kadın") if sonuc.endswith(" W") else sonuc
    sonuc = sonuc.replace("U20", "U20")
    sonuc = sonuc.replace("U21", "U21")
    sonuc = sonuc.replace("U23", "U23")

    return sonuc


def mac_id_uret(lig, ev, dep):
    return hashlib.md5(f"{lig}|{ev}|{dep}".encode("utf-8")).hexdigest()[:12]


def api_get(url, params):
    try:
        r = requests.get(url, params=params, timeout=25)
        data = r.json()

        print("API durum:", r.status_code)
        print("Kullanılan:", r.headers.get("x-requests-used"))
        print("Kalan:", r.headers.get("x-requests-remaining"))

        if r.status_code != 200:
            print("API atlandı:", data)
            return None

        if isinstance(data, dict):
            print("API atlandı:", data)
            return None

        return data

    except Exception as e:
        print("API hata:", e)
        return None


def cache_yukle():
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def cache_kaydet(maclar):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "zaman": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "maclar": maclar
        }, f, ensure_ascii=False, indent=2)


def mac_bul_id(mac_id):
    cache = cache_yukle()
    if not cache:
        return None
    for m in cache["maclar"]:
        if m["id"] == mac_id:
            return m
    return None


def oranlari_cek():
    sporlar = api_get("https://api.the-odds-api.com/v4/sports", {"apiKey": ODDS_API_KEY})
    if not sporlar:
        return []

    maclar = {}

    for spor in sporlar:
        lig = spor.get("key", "")

        if not spor.get("active") or not lig.startswith("soccer_"):
            continue

        print("Lig deneniyor:", lig)

        for market in ["h2h", "totals", "btts"]:
            data = api_get(
                f"https://api.the-odds-api.com/v4/sports/{lig}/odds",
                {
                    "apiKey": ODDS_API_KEY,
                    "regions": BOLGE,
                    "markets": market,
                    "oddsFormat": "decimal"
                }
            )

            if not data:
                continue

            for event in data:
                ev = event.get("home_team")
                dep = event.get("away_team")

                if not ev or not dep:
                    continue

                mid = mac_id_uret(lig, ev, dep)

                if mid not in maclar:
                    maclar[mid] = {
                        "id": mid,
                        "lig": lig,
                        "ev": ev,
                        "dep": dep,
                        "bahis_sitesi": "Bilinmiyor",
                        "ms": {},
                        "alt_ust": {},
                        "kg": {}
                    }

                for bookmaker in event.get("bookmakers", []):
                    site = bookmaker.get("title", "Bilinmiyor")

                    for mk in bookmaker.get("markets", []):
                        if mk.get("key") == "h2h":
                            for o in mk.get("outcomes", []):
                                ad = str(o.get("name", ""))
                                fiyat = o.get("price")
                                if fiyat is None:
                                    continue

                                if ad == ev:
                                    maclar[mid]["ms"]["1"] = float(fiyat)
                                elif ad == dep:
                                    maclar[mid]["ms"]["2"] = float(fiyat)
                                elif ad.lower() == "draw":
                                    maclar[mid]["ms"]["X"] = float(fiyat)

                                maclar[mid]["bahis_sitesi"] = site

                        elif mk.get("key") == "totals":
                            for o in mk.get("outcomes", []):
                                ad = str(o.get("name", "")).lower()
                                puan = o.get("point")
                                fiyat = o.get("price")
                                if puan is None or fiyat is None:
                                    continue

                                puan = str(float(puan))

                                if puan not in maclar[mid]["alt_ust"]:
                                    maclar[mid]["alt_ust"][puan] = {}

                                if ad == "over":
                                    maclar[mid]["alt_ust"][puan]["üst"] = float(fiyat)
                                elif ad == "under":
                                    maclar[mid]["alt_ust"][puan]["alt"] = float(fiyat)

                                maclar[mid]["bahis_sitesi"] = site

                        elif mk.get("key") == "btts":
                            for o in mk.get("outcomes", []):
                                ad = str(o.get("name", "")).lower()
                                fiyat = o.get("price")
                                if fiyat is None:
                                    continue

                                if ad == "yes":
                                    maclar[mid]["kg"]["var"] = float(fiyat)
                                elif ad == "no":
                                    maclar[mid]["kg"]["yok"] = float(fiyat)

                                maclar[mid]["bahis_sitesi"] = site

    temiz = []
    for m in maclar.values():
        if m["ms"] or m["alt_ust"] or m["kg"]:
            temiz.append(m)

    print("Toplam maç:", len(temiz))
    return temiz


def mac_ara(sorgu):
    cache = cache_yukle()
    if not cache:
        return []

    q = temiz_yazi(sorgu)
    sonuc = []

    for m in cache["maclar"]:
        if q in temiz_yazi(m["ev"]) or q in temiz_yazi(m["dep"]):
            sonuc.append(m)

    return sonuc[:10]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ Bot aktif.\n\n"
        "Önce /guncelle yaz.\n"
        "Sonra takım adı yaz: kanada, real madrid, galatasaray\n\n"
        "/kupon → kuponu gösterir\n"
        "/temizle → kuponu siler\n"
        "/durum → veri durumunu gösterir"
    )


async def guncelle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Oranlar çekiliyor...")

    maclar = oranlari_cek()

    if not maclar:
        await update.message.reply_text("❌ Oran çekilemedi. CMD hata çıktısını gönder.")
        return

    cache_kaydet(maclar)

    await update.message.reply_text(
        f"✅ Güncellendi.\n"
        f"Toplam maç: {len(maclar)}\n"
        f"Artık kupon sorguları kredi harcamaz."
    )


async def durum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cache = cache_yukle()
    if not cache:
        await update.message.reply_text("Veri yok. Önce /guncelle yaz.")
        return

    await update.message.reply_text(
        f"📁 Son güncelleme: {cache['zaman']}\n"
        f"Maç sayısı: {len(cache['maclar'])}"
    )


async def temizle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kullanici_kuponlari[update.message.chat_id] = []
    await update.message.reply_text("🗑️ Kupon temizlendi.")


async def mesaj_yakala(update: Update, context: ContextTypes.DEFAULT_TYPE):
    maclar = mac_ara(update.message.text)

    if not maclar:
        await update.message.reply_text("❌ Maç bulunamadı.")
        return

    for m in maclar:
        butonlar = [[
            InlineKeyboardButton("🎯 Taraf", callback_data=f"taraf|{m['id']}"),
            InlineKeyboardButton("📊 Alt / Üst", callback_data=f"altust|{m['id']}"),
            InlineKeyboardButton("⚽ KG", callback_data=f"kg|{m['id']}")
        ]]

        await update.message.reply_text(
            f"⚽ {turkce_ad(m['ev'])} - {turkce_ad(m['dep'])}\n🏦 {m['bahis_sitesi']}",
            reply_markup=InlineKeyboardMarkup(butonlar)
        )


async def buton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    parca = q.data.split("|")
    islem = parca[0]
    mid = parca[1]

    mac = mac_bul_id(mid)
    if not mac:
        await q.message.reply_text("❌ Maç verisi bulunamadı.")
        return

    chat_id = q.message.chat_id
    if chat_id not in kullanici_kuponlari:
        kullanici_kuponlari[chat_id] = []

    mac_adi = f"{turkce_ad(mac['ev'])} - {turkce_ad(mac['dep'])}"

    if islem == "taraf":
        b = []
        if "1" in mac["ms"]:
            b.append(InlineKeyboardButton(f"1 ({mac['ms']['1']})", callback_data=f"sec|{mid}|MS 1|{mac['ms']['1']}"))
        if "X" in mac["ms"]:
            b.append(InlineKeyboardButton(f"X ({mac['ms']['X']})", callback_data=f"sec|{mid}|MS X|{mac['ms']['X']}"))
        if "2" in mac["ms"]:
            b.append(InlineKeyboardButton(f"2 ({mac['ms']['2']})", callback_data=f"sec|{mid}|MS 2|{mac['ms']['2']}"))

        if not b:
            await q.message.reply_text("Bu maçta taraf oranı yok.")
            return

        await q.message.reply_text("🎯 Taraf seç:", reply_markup=InlineKeyboardMarkup([b]))

    elif islem == "altust":
        cizgiler = ["0.5", "1.5", "2.5", "3.5", "4.5", "5.5"]
        satirlar = []

        for c in cizgiler:
            satirlar.append([InlineKeyboardButton(c, callback_data=f"cizgi|{mid}|{c}")])

        await q.message.reply_text("📊 Gol çizgisi seç:", reply_markup=InlineKeyboardMarkup(satirlar))

    elif islem == "cizgi":
        p = parca[2]
        oranlar = mac["alt_ust"].get(str(float(p)), {})
        b = [
            InlineKeyboardButton("Üst", callback_data=f"altustsec|{mid}|{p}|üst"),
            InlineKeyboardButton("Alt", callback_data=f"altustsec|{mid}|{p}|alt")
        ]

        await q.message.reply_text(f"📊 {p} için seçim yap:", reply_markup=InlineKeyboardMarkup([b]))

    elif islem == "altustsec":
        p = parca[2]
        secim_turu = parca[3]
        oranlar = mac["alt_ust"].get(str(float(p)), {})

        if secim_turu not in oranlar:
            await q.message.reply_text(f"❌ Bu maçta {p} {secim_turu} oranı yok.")
            return

        oran = oranlar[secim_turu]
        secim = f"{p} {secim_turu.capitalize()}"

        kullanici_kuponlari[chat_id].append({
            "mac": mac_adi,
            "secim": secim,
            "oran": oran
        })

        await q.message.reply_text(f"✅ Kupona eklendi:\n{mac_adi}\n{secim}: {oran}")

    elif islem == "kg":
        b = []

        if "var" in mac["kg"]:
            b.append(InlineKeyboardButton(f"Var ({mac['kg']['var']})", callback_data=f"sec|{mid}|KG Var|{mac['kg']['var']}"))
        if "yok" in mac["kg"]:
            b.append(InlineKeyboardButton(f"Yok ({mac['kg']['yok']})", callback_data=f"sec|{mid}|KG Yok|{mac['kg']['yok']}"))

        if not b:
            await q.message.reply_text("Bu maçta KG oranı yok.")
            return

        await q.message.reply_text("⚽ KG seç:", reply_markup=InlineKeyboardMarkup([b]))

    elif islem == "sec":
        secim = parca[2]
        oran = float(parca[3])

        kullanici_kuponlari[chat_id].append({
            "mac": mac_adi,
            "secim": secim,
            "oran": oran
        })

        await q.message.reply_text(f"✅ Kupona eklendi:\n{mac_adi}\n{secim}: {oran}")


async def kupon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    kupon = kullanici_kuponlari.get(chat_id, [])

    if not kupon:
        await update.message.reply_text("Kupon boş.")
        return

    toplam = 1
    mesaj = "📊 Kupon\n\n"

    for k in kupon:
        toplam *= k["oran"]
        mesaj += f"⚽ {k['mac']}\n➡️ {k['secim']}: {k['oran']}\n\n"

    mesaj += f"🎯 Toplam oran: {round(toplam, 2)}"

    await update.message.reply_text(mesaj)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("guncelle", guncelle))
    app.add_handler(CommandHandler("durum", durum))
    app.add_handler(CommandHandler("temizle", temizle))
    app.add_handler(CommandHandler("kupon", kupon))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_yakala))
    app.add_handler(CallbackQueryHandler(buton))

    print("Bot çalışıyor...")
    app.run_polling()


if __name__ == "__main__":
    main()