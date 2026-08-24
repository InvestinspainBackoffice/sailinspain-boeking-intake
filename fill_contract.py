#!/usr/bin/env python3
"""
Fill Sail in Spain contract template with booking data.
Creates a client folder in Dropbox and saves the filled contract.

Usage:
    python3 fill_contract.py '{"name":"Jan Jansen","address":"Straat 1, Amsterdam",...}'

Or import and call fill_contract(data_dict) directly.
"""

import json
import sys
import os
import shutil
import zipfile
from docx import Document


TEMPLATE_PATH = os.path.expanduser(
    "~/INVESTINSPAIN Dropbox/Sam Steylaerts/Facu & Lucy/06 Clients/"
    "SAILINSPAIN template contract clients_sjabloon.dotx"
)
CLIENTS_DIR = os.path.expanduser(
    "~/INVESTINSPAIN Dropbox/Sam Steylaerts/Facu & Lucy/06 Clients/Client contracts"
)


def load_dotx_as_docx(dotx_path):
    tmp = "/tmp/_sis_template.docx"
    shutil.copy2(dotx_path, tmp)
    with zipfile.ZipFile(tmp, 'r') as zin:
        content = {n: zin.read(n) for n in zin.namelist()}
    ct = content['[Content_Types].xml']
    ct = ct.replace(
        b'wordprocessingml.template.main+xml',
        b'wordprocessingml.document.main+xml'
    )
    content['[Content_Types].xml'] = ct
    with zipfile.ZipFile(tmp, 'w') as zout:
        for name, data in content.items():
            zout.writestr(name, data)
    return Document(tmp)


def replace_in_runs(paragraph, old, new):
    full = paragraph.text
    if old not in full:
        return False
    replaced = full.replace(old, new, 1)
    for i, run in enumerate(paragraph.runs):
        if i == 0:
            run.text = replaced
        else:
            run.text = ""
    return True


def format_date(iso_date):
    if not iso_date:
        return ""
    parts = iso_date.split("-")
    if len(parts) == 3:
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    return iso_date


def build_date_str(date_from, date_to):
    if not date_from:
        return "[●]"
    f = format_date(date_from)
    if date_to and date_to != date_from:
        t = format_date(date_to)
        return f"{f} – {t}"
    return f


def check_food_items(text, selected_foods):
    food_map = {
        "Mediterranean breakfast board": "Mediterranean breakfast board",
        "Chicken salad": "Chicken salad",
        "Pasta deluxe (prawns)": "Pasta deluxe (prawns)",
        "Paella": "Paella",
        "Tapas board – luxury version": "Tapas board – luxury version",
        "Fresh Tortilla": "Fresh Tortilla",
        "Tiramisu": "Tiramisu",
        "Fresh fruit": "Fresh fruit",
    }
    for item_key, item_label in food_map.items():
        if any(item_key.lower() in s.lower() for s in selected_foods):
            text = text.replace(f"☐ {item_label}", f"☑ {item_label}")
    return text


def check_drink_items(text, selected_drinks):
    drink_map = {
        "Wine": "Wine (Rosé, Red, White)",
        "Cava": "Cava",
        "Champagne": "Champagne",
        "Gin & tonic": "Gin & tonic",
        "Vodka + fresh orange": "Vodka + fresh orange",
        "Mojito": "Mojito",
    }
    for item_key, item_label in drink_map.items():
        if any(item_key.lower() in s.lower() for s in selected_drinks):
            text = text.replace(f"☐ {item_label}", f"☑ {item_label}")
    return text


def fill_contract(data):
    doc = load_dotx_as_docx(TEMPLATE_PATH)

    name = data.get("name", "")
    address = data.get("address", "")
    idnr = data.get("idnr", "")
    port = data.get("port", "")
    date_from = data.get("dateFrom", "")
    date_to = data.get("dateTo", "")
    time_start = data.get("timeStart", "10:00")
    time_end = data.get("timeEnd", "18:00")
    guests = data.get("guests", "")
    total_raw = data.get("total", "")
    # Guard: if total looks like a time value (HH:MM), ignore it
    total = total_raw if total_raw and ":" not in str(total_raw) else ""
    deposit = data.get("deposit", "0")
    foods = [f.strip() for f in data.get("foods", "").split(",") if f.strip()]
    drinks = [d.strip() for d in data.get("drinks", "").split(",") if d.strip()]
    wine = data.get("wine", "")
    bubbly = data.get("bubbly", "")
    special = data.get("special", "")
    catcost = data.get("catcost", "")

    date_str = build_date_str(date_from, date_to)

    for p in doc.paragraphs:
        text = p.text

        # Section 1: Client info
        if "Name: [●]" in text:
            new_text = text.replace("Name: [●]", f"Name: {name}")
            new_text = new_text.replace("Address: [●]", f"Address: {address}")
            new_text = new_text.replace("ID / Passport: [●]", f"ID / Passport: {idnr}")
            for i, run in enumerate(p.runs):
                run.text = new_text if i == 0 else ""

        # Section 2: Charter details - Port
        if "☐ Sotogrande" in text and "☐ Puerto Banús" in text:
            if port == "Sotogrande":
                new_text = text.replace("☐ Sotogrande", "☑ Sotogrande")
            elif "Banús" in port or "Banus" in port:
                new_text = text.replace("☐ Puerto Banús", "☑ Puerto Banús")
            else:
                new_text = text
            for i, run in enumerate(p.runs):
                run.text = new_text if i == 0 else ""

        # Section 2: Date, Time, Guests
        if "Date: [●]" in text:
            new_text = text.replace("Date: [●]", f"Date: {date_str}")
            new_text = new_text.replace("Time: [●] – [●]", f"Time: {time_start} – {time_end}")
            new_text = new_text.replace("Guests: [●]", f"Guests: {guests}")
            for i, run in enumerate(p.runs):
                run.text = new_text if i == 0 else ""

        # Section 5: Total price
        if "Total price: € [●]" in text:
            replace_in_runs(p, "Total price: € [●]", f"Total price: € {total}")

        # Section 12: Security deposit
        if "Deposit: € [●]" in text:
            replace_in_runs(p, "Deposit: € [●]", f"Deposit: € {deposit}")

        # Annex: Client name & date
        if "Client name: [●]" in text:
            new_text = text.replace("Client name: [●]", f"Client name: {name}")
            new_text = new_text.replace("Date: [●]", f"Date: {date_str}")
            for i, run in enumerate(p.runs):
                run.text = new_text if i == 0 else ""

        # Annex: Food checkboxes
        if "☐ Mediterranean breakfast board" in text:
            new_text = check_food_items(text, foods)
            for i, run in enumerate(p.runs):
                run.text = new_text if i == 0 else ""

        # Annex: Drink checkboxes
        if "☐ Wine (Rosé, Red, White)" in text:
            new_text = check_drink_items(text, drinks)
            for i, run in enumerate(p.runs):
                run.text = new_text if i == 0 else ""

        # Annex: Wine & Cava details
        if "In case of Wine" in text:
            new_text = text
            if wine:
                new_text = new_text.replace(
                    "In case of Wine please note how many bottles and Rosé, Red or White: ___________",
                    f"In case of Wine please note how many bottles and Rosé, Red or White: {wine}"
                )
            if bubbly:
                new_text = new_text.replace(
                    "Cava or Champagne will always be white, please define how many bottles: ___________",
                    f"Cava or Champagne will always be white, please define how many bottles: {bubbly}"
                )
            for i, run in enumerate(p.runs):
                run.text = new_text if i == 0 else ""

        # Annex: Special requests
        if "Special requests: ___________" in text:
            if special:
                replace_in_runs(p, "Special requests: ___________", f"Special requests: {special}")

        # Annex: Total extras (catering cost) — always leave blank
        # Price varies per trip and is filled in manually

    # Create client folder
    folder_name = name.strip() if name.strip() else "Onbekend"
    client_dir = os.path.join(CLIENTS_DIR, folder_name)
    os.makedirs(client_dir, exist_ok=True)

    # Save contract
    filename = f"SAILINSPAIN_Contract_{folder_name.replace(' ', '_')}.docx"
    output_path = os.path.join(client_dir, filename)
    doc.save(output_path)

    print(f"Contract aangemaakt: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fill_contract.py '{\"name\":\"...\", ...}'")
        sys.exit(1)
    data = json.loads(sys.argv[1])
    fill_contract(data)
