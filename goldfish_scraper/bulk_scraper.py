import requests
import re
import urllib3
import matplotlib.pyplot as plt
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://www.mtggoldfish.com/price_history_component"

CARDS = [
    "Ocelot Pride [MH3]",
    "Phyrexian Tower [MH3]",
    "Warren Soultrader [MH3]",
    "Urza's Incubator [MH3]",
    "Ulamog, the Defiler [MH3]",
    "Polluted Delta [MH3]",
    "Bloodstained Mire [MH3]",
    "Jet Medallion [MH3]"
]


def fetch_history(card_id):
    params = {
        "card_id": card_id,
        "selector": "#tab-paper",
        "type": "paper",
        "price_type": "card",
    }

    r = requests.get(
        URL,
        params=params,
        headers={"User-Agent": "Mozilla/5.0"},
        verify=False,
        timeout=30
    )

    r.raise_for_status()

    price_lines = re.findall(
        r'd \+= "\\n([^"]+)"',
        r.text
    )

    history = []

    for line in price_lines:
        date_str, price_str = [x.strip() for x in line.split(",")]

        history.append({
            "date": datetime.strptime(date_str, "%Y-%m-%d"),
            "price": float(price_str)
        })

    return history


plt.figure(figsize=(14, 8))

for card in CARDS:
    try:
        history = fetch_history(card)

        dates = [row["date"] for row in history]
        prices = [row["price"] for row in history]

        plt.plot(
            dates,
            prices,
            linewidth=2,
            label=card
        )

        print(f"Loaded {card}: {len(history)} points")

    except Exception as e:
        print(f"Failed: {card} - {e}")

plt.title("MTGGoldfish Price History Comparison")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()