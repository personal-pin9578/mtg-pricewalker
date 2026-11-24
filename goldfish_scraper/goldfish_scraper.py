import requests
import re
import time

url = "https://www.mtggoldfish.com/price_history_component"

params = {
    "card_id": "Old Gnawbone [AFR]",
    "selector": "#tab-paper",
    "type": "paper",
    "price_type": "card",
}

r = requests.get(
    url,
    params=params,
    headers={"User-Agent": "Mozilla/5.0"},
    verify = False
)

print(r.status_code)

price_lines = re.findall(
    r'd \+= "\\n([^"]+)"',
    r.text
)

history = []

for line in price_lines:
    date_str, price_str = [x.strip() for x in line.split(",")]

    history.append({
        "date": date_str,
        "price": float(price_str)
    })

# print(history)


import matplotlib.pyplot as plt
from datetime import datetime

dates = [
    datetime.strptime(row["date"], "%Y-%m-%d")
    for row in history
]

prices = [
    row["price"]
    for row in history
]

plt.figure(figsize=(12, 6))
plt.plot(dates, prices, linewidth=1.5)

plt.title("Price History")
plt.xlabel("Date")
plt.ylabel("Price (USD)")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()