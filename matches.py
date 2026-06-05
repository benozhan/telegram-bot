import requests
from datetime import datetime, timedelta

API_KEY = "1e9d0e3b90a70db602a98f4c1090bce9"

odds_url = "https://v3.football.api-sports.io/odds"
fixtures_url = "https://v3.football.api-sports.io/fixtures"

headers = {
    "x-apisports-key": API_KEY
}

all_odds = []
all_fixtures = []

for i in range(7):
    date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")

    odds_data = requests.get(
        odds_url,
        headers=headers,
        params={
            "date": date,
            "bookmaker": "8",
            "bet": "1"
        }
    ).json()

    fixture_data = requests.get(
        fixtures_url,
        headers=headers,
        params={
            "date": date
        }
    ).json()

    all_odds.extend(odds_data.get("response", []))
    all_fixtures.extend(fixture_data.get("response", []))

teams = {}

for item in all_fixtures:
    fid = str(item["fixture"]["id"])

    home = item["teams"]["home"]["name"]
    away = item["teams"]["away"]["name"]

    teams[fid] = (home, away)

odds_map = {}

print("\nMAÇLAR:\n")

for item in all_odds:
    try:
        fid = str(item["fixture"]["id"])

        values = item["bookmakers"][0]["bets"][0]["values"]

        home_team, away_team = teams.get(
            fid,
            ("Bilinmiyor", "Bilinmiyor")
        )

        odds_map[fid] = {
            "Home": float(values[0]["odd"]),
            "Draw": float(values[1]["odd"]),
            "Away": float(values[2]["odd"]),
            "home_team": home_team,
            "away_team": away_team
        }

        print(
            f"{fid} | {home_team} - {away_team}"
        )
        print(
            f"Home: {values[0]['odd']} | Draw: {values[1]['odd']} | Away: {values[2]['odd']}"
        )
        print("-" * 50)

    except:
        pass

print("\nKupon oluştur.")
print("Örnek:")
print("Argentina W")
print("Paraguay W")
print("draw Chile W")
print("Bitirmek için boş Enter.\n")

total = 1

while True:
    line = input("Seçim: ").strip()

    if line == "":
        break

    query = line.lower()
    want_draw = False

    if query.startswith("draw "):
        want_draw = True
        query = query.replace("draw ", "", 1)

    found = False

    for info in odds_map.values():

        home = info["home_team"].lower()
        away = info["away_team"].lower()

        if query in home:

            pick = "Draw" if want_draw else "Home"

            odd = info[pick]

            total *= odd

            print(
                f"{info['home_team']} - {info['away_team']} | {pick}: {odd}"
            )

            found = True
            break

        if query in away:

            pick = "Draw" if want_draw else "Away"

            odd = info[pick]

            total *= odd

            print(
                f"{info['home_team']} - {info['away_team']} | {pick}: {odd}"
            )

            found = True
            break

    if not found:
        print("Maç bulunamadı.")

print(f"\nToplam oran: {round(total, 2)}")