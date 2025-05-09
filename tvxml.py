import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom
import html
import sys

# Remove all quote-like characters
def remove_quotes(text):
    return text.replace('"', '').replace('“', '').replace('”', '').replace('„', '').replace("'", '').strip()

# Load channel definitions
with open("channels.json", "r", encoding="utf-8") as f:
    channels = json.load(f)["tv_channels"]

# Prepare 3 days
base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
date_list = [base_date + timedelta(days=i) for i in range(3)]
date_params = [(d.strftime("%d.%m"), d) for d in date_list]

# XMLTV root
tv = ET.Element("tv", {
    "generator-info-name": "EPG",
    "generation-date": base_date.strftime("%d.%m.%Y"),
    "generator-info-url": "http://tv.lanbg.com"
})

# Convert HH.MM to datetime for a given day
def parse_time(time_str, day_obj):
    h, m = map(int, time_str.split("."))
    return day_obj.replace(hour=h, minute=m, second=0, microsecond=0)

# Progress bar helper
def print_progress(current, total, channel_name):
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f"\rProgress: |{bar}| {current}/{total} channels - Processing: {channel_name}")
    sys.stdout.flush()

# Process each channel
for index, ch in enumerate(channels, start=1):
    print_progress(index, len(channels), ch["name"])

    ch_id = ch["name"]
    ET.SubElement(ET.SubElement(tv, "channel", {"id": ch_id}), "display-name", {"lang": "bg"}).text = ch_id
    ET.SubElement(tv.find(f"./channel[@id='{ch_id}']"), "icon", {"src": f"http://tv.lanbg.com/{ch_id.lower()}.png"})

    combined_entries = []

    for dd_str, day_obj in date_params:
        source = ch.get("source", "dir.bg")

        if source == "dir.bg":
            url = f"https://tv.dir.bg/tv_channel.php?id={ch['id']}&dd={dd_str}"
            html_doc = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
            soup = BeautifulSoup(html_doc, "html.parser")
            entries = soup.select("ul#events > li")

            for e in entries:
                time_tag = e.find("i")
                if not time_tag:
                    continue
                time_str = time_tag.text.strip()
                full_text = e.get_text(strip=True, separator=" ")
                desc = full_text[len(time_str):].strip()

                parts = desc.split('-', 1)
                if len(parts) == 2:
                    title = parts[0].strip()
                    desc = parts[1].strip()
                else:
                    title = desc
                    desc = ""

                combined_entries.append({
                    "time": time_str,
                    "title": title,
                    "desc": desc,
                    "origin_date": day_obj
                })

        elif source == "dnevnik.bg":
            url = f"https://www.dnevnik.bg/sled5/tv/{ch['id']}_{ch['name'].lower()}/{day_obj.strftime('%Y%m%d')}/"
            html_doc = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
            soup = BeautifulSoup(html_doc, "html.parser")
            rows = soup.select("table.expanded tr")

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 2:
                    continue
                time_str = cols[0].get_text(strip=True).replace(":", ".")
                desc = cols[1].get_text(strip=True)

                parts = desc.split('-', 1)
                if len(parts) == 2:
                    title = parts[0].strip()
                    desc = parts[1].strip()
                else:
                    title = desc
                    desc = ""

                combined_entries.append({
                    "time": time_str,
                    "title": title,
                    "desc": desc,
                    "origin_date": day_obj
                })

    if not combined_entries:
        continue

    # Sort and track broadcast day rollover
    schedule = []
    current_day = combined_entries[0]["origin_date"]
    previous_dt = None

    for item in combined_entries:
        proposed_dt = parse_time(item["time"], current_day)
        if previous_dt and proposed_dt < previous_dt:
            current_day += timedelta(days=1)
            proposed_dt = parse_time(item["time"], current_day)

        item_dt = proposed_dt
        schedule.append({
            "start": item_dt,
            "title": item["title"],
            "desc": item["desc"]
        })
        previous_dt = item_dt

    # Emit <programme>
    for i, item in enumerate(schedule):
        start = item["start"]
        end = schedule[i + 1]["start"] if i + 1 < len(schedule) else start + timedelta(minutes=60)
        start_fmt = start.strftime("%Y%m%d%H%M%S +0300")
        end_fmt = end.strftime("%Y%m%d%H%M%S +0300")

        prog = ET.SubElement(tv, "programme", {
            "start": start_fmt,
            "stop": end_fmt,
            "channel": ch_id
        })
        ET.SubElement(prog, "title", {"lang": "bg"}).text = remove_quotes(html.unescape(item["title"]))
        desc_text = remove_quotes(html.unescape(item["desc"]))
        if desc_text:
            ET.SubElement(prog, "desc", {"lang": "bg"}).text = desc_text

# Pretty-print and save
rough_string = ET.tostring(tv, encoding="utf-8")
reparsed = minidom.parseString(rough_string)
pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

with open("/var/www/html/epg/tv_schedule.xml", "wb") as f:
    f.write(pretty_xml)

print("\n✅ tv_schedule.xml with broadcast-day rollover generated.")
