import re
import requests
import urllib3
import matplotlib.pyplot as plt

from datetime import datetime
from urllib.parse import unquote_plus

# ========================================================
# CONFIG
# ========================================================

CARDS = [
    "Ghave, Guru of Spores [2X2] 216",
    "Mirage Mirror [M3C] 300",
    "Arwen, Weaver of Hope [LTC] 35"
]

HEADERS = {
    "User-Agent":
        "goldfish-scraper/0.1 (pietro.spinelli1998@gmail.com)"
}

SCRYFALL_URL = "https://api.scryfall.com/cards/search"

PRICE_HISTORY_URL = (
    "https://www.mtggoldfish.com/price_history_component"
)

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# ========================================================
# HELPERS
# ========================================================

def slugify(text):
    text = text.lower()

    text = re.sub(
        r"[^\w\s-]",
        "",
        text
    )

    text = re.sub(
        r"\s+",
        "-",
        text
    )

    return text.strip("-")


def parse_card(card_string):

    match = re.match(
        r"(.+?)\s+\[([A-Z0-9]+)\]\s+(\S+)$",
        card_string
    )

    if not match:
        raise ValueError(
            f"Could not parse card: {card_string}"
        )

    return {
        "name": match.group(1),
        "set_code": match.group(2).lower(),
        "collector_number": match.group(3)
    }


# ========================================================
# SCRYFALL
# ========================================================

def get_scryfall_card(card_name, set_code):

    query = f'!"{card_name}" set:{set_code}'

    r = requests.get(
        SCRYFALL_URL,
        params={"q": query},
        headers=HEADERS,
        verify=False,
        timeout=30
    )

    r.raise_for_status()

    payload = r.json()

    if "data" not in payload:
        raise RuntimeError(payload)

    return payload["data"][0]


# ========================================================
# MTGGOLDFISH
# ========================================================

def build_goldfish_url(card):
    print(card['set_name'])
    match card['set_name']:
        case 'Tales of Middle-earth Commander':
            print("OMG OMG")
            card['set_name'] = "The Lord Of The Rings Tales of Middle Earth commander"           

    return (
        "https://www.mtggoldfish.com/price/"
        f"{slugify(card['set_name'])}/"
        f"{card['collector_number']}/"
        f"{slugify(card['name'])}"
    )


def get_goldfish_card_id(card):

    url = build_goldfish_url(card)

    print(f"\nResolving: {url}")

    html = requests.get(
        url,
        headers=HEADERS,
        verify=False,
        timeout=30
    ).text

    matches = re.findall(
        r'card_id=([^"&]+)',
        html
    )

    card_ids = list({
        unquote_plus(m)
        for m in matches
    })

    print("Found card_ids:")

    for cid in card_ids:
        print(f"    {cid}")

    set_code = card["set"].upper()

    for cid in card_ids:

        if f"[{set_code}]" not in cid:
            continue

        if cid.startswith(card["name"]):

            print(f"Resolved card_id:")
            print(f"    {cid}")

            return cid

    raise RuntimeError(
        f"Could not resolve MTGGoldfish ID for "
        f"{card['name']}"
    )


# ========================================================
# PRICE HISTORY
# ========================================================

def fetch_history(card_id):

    params = {
        "card_id": card_id,
        "selector": "#tab-paper",
        "type": "paper",
        "price_type": "card",
    }

    r = requests.get(
        PRICE_HISTORY_URL,
        params=params,
        headers=HEADERS,
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

        try:

            date_str, price_str = [
                x.strip()
                for x in line.split(",")
            ]

            history.append({
                "date": datetime.strptime(
                    date_str,
                    "%Y-%m-%d"
                ),
                "price": float(price_str)
            })

        except Exception:
            continue

    return history


# ========================================================
# MAIN
# ========================================================

plt.figure(figsize=(15, 8))

for card_string in CARDS:

    try:

        card_info = parse_card(card_string)

        scryfall_card = get_scryfall_card(
            card_info["name"],
            card_info["set_code"]
        )

        card_id = get_goldfish_card_id(
            scryfall_card
        )

        history = fetch_history(
            card_id
        )

        print(
            f"History rows: {len(history)}"
        )

        if not history:
            continue

        dates = [
            row["date"]
            for row in history
        ]

        prices = [
            row["price"]
            for row in history
        ]

        base_price = prices[0]

        normalized_prices = [
            (price / base_price) * 100
            for price in prices
        ]

        plt.plot(
            dates,
            normalized_prices,
            linewidth=2,
            label=scryfall_card["name"]
        )

        print(
            f"Loaded {scryfall_card['name']}"
        )

    except Exception as e:

        print(
            f"\nFAILED: {card_string}"
        )

        print(e)


# ========================================================
# PLOT
# ========================================================

plt.title(
    "MTGGoldfish Price Performance"
)

plt.xlabel(
    "Date"
)

plt.ylabel(
    "Indexed Price (100 = Initial Value)"
)

plt.grid(
    True,
    alpha=0.3
)

plt.legend()

plt.tight_layout()

plt.show()