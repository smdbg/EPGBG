import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom
import html
import sys
import time
from io import BytesIO

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
    "generator-info-url": "http://tv.com"
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

# Load external XMLTV for fallback
try:
    response = requests.get("https://raw.githubusercontent.com/harrygg/EPG/refs/heads/master/all-3days.full.epg.xml",timeout=30)
    external_tree = ET.parse(BytesIO(response.content))
    external_root = external_tree.getroot()
except Exception as e:
    print(f"\n⚠️ Failed to load external XMLTV: {e}")
    external_root = None

# Process each channel
for index, ch in enumerate(channels, start=1):
    ch_id = ch["xml"]
    print_progress(index, len(channels), ch_id)

    ET.SubElement(ET.SubElement(tv, "channel", {"id": ch_id}), "display-name", {"lang": "bg"}).text = ch_id
    ET.SubElement(tv.find(f"./channel[@id='{ch_id}']"), "icon", {"src": f"http://tv.com/{ch_id.lower()}.png"})

    combined_entries = []

    for dd_str, day_obj in date_params:
        day_entries = []
        for source_def in ch.get("sources", []):
            source = source_def.get("source")
            try:
                if source == "dir.bg":
                   url = f"https://tv.dir.bg/programa/{source_def['id']}"
                   html_doc = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
                   soup = BeautifulSoup(html_doc, "html.parser")
                   panels = soup.select("div.panel")
                   label_to_day = {
                           "Вчера": base_date - timedelta(days=1),
                           "Днес": base_date,
                           "Утре": base_date + timedelta(days=1),
                            }
                   for panel in panels:
                      day_section = panel.select_one("div.day-broadcast-list")
                      if not day_section:
                         continue
                      label = day_section.find("p", class_="broadcast-item-name")
                      if not label:
                         continue
                      label_text = label.get_text(strip=True)
                      entry_day = label_to_day.get(label_text)
                      if entry_day != day_obj:
                         continue
                      for item in day_section.select("div.broadcast-item"):
                           time_tag = item.find("div", class_="broadcast-time")
                           title_tag = item.find("div", class_="broadcast-title")
                           if not time_tag or not title_tag:
                                 continue
                           time_str = time_tag.text.strip().replace(":", ".")
                           desc_full = title_tag.get_text(strip=True)
                           parts = desc_full.split(',', 1)
                           title = parts[0].strip()
                           desc = parts[1].strip() if len(parts) == 2 else ""
                           day_entries.append({"time": time_str, "title": title, "desc": desc, "origin_date": day_obj})
                   break
                elif source == "dnevnik.bg":
                    url = f"https://www.dnevnik.bg/sled5/tv/{source_def['id']}_{source_def['name']}/{day_obj.strftime('%Y%m%d')}/"
                    html_doc = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
                    soup = BeautifulSoup(html_doc, "html.parser")
                    rows = soup.select("table.expanded tr")
                    for row in rows:
                        cols = row.find_all("td")
                        if len(cols) < 2:
                            continue
                        time_str = cols[0].get_text(strip=True).replace(":", ".")
                        desc = cols[1].get_text(strip=True)
                        parts = desc.split('-', 1)
                        title = parts[0].strip() if len(parts) == 2 else desc
                        desc = parts[1].strip() if len(parts) == 2 else ""
                        day_entries.append({"time": time_str, "title": title, "desc": desc, "origin_date": day_obj})
                    break

                elif source == "start.bg":
                    url = f"https://www.start.bg/lenta/tv-programa//tv/show/channel/{source_def['id']}/{day_obj.strftime('%Y-%m-%d')}/0"
                    html_doc = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
                    soup = BeautifulSoup(html_doc, "html.parser")
                    items = soup.select("ul.tv-dlist li")
                    for item in items:
                        time_div = item.find("div", class_="time")
                        title_div = item.find("div", class_="title")
                        if not time_div or not title_div:
                            continue
                        time_text = time_div.text.strip()
                        if time_text == "Сега":
                            now = datetime.now()
                            time_str = now.strftime("%H.%M")
                        else:
                            time_str = time_text.replace(":", ".")
                        desc = title_div.get_text(strip=True)
                        parts = desc.split('-', 1)
                        title = parts[0].strip() if len(parts) == 2 else desc
                        desc = parts[1].strip() if len(parts) == 2 else ""
                        day_entries.append({"time": time_str, "title": title, "desc": desc, "origin_date": day_obj})
                    break

                elif source == "harrygg" and external_root is not None:
                    xmltv_id = source_def["name"]
                    for prog in external_root.findall(f"programme[@channel='{xmltv_id}']"):
                        start_str = prog.get("start")
                        dt = datetime.strptime(start_str[:14], "%Y%m%d%H%M%S")
                        if dt.date() != day_obj.date():
                            continue
                        title = prog.findtext("title", default="").strip()
                        desc = prog.findtext("desc", default="").strip()
                        time_str = dt.strftime("%H.%M")
                        day_entries.append({"time": time_str, "title": title, "desc": desc, "origin_date": day_obj})
                    break

            except requests.RequestException:
                print(f"\n⚠️ Failed channel: {ch_id} from {source}")
                continue

        combined_entries.extend(day_entries)

    if not combined_entries:
        continue

    schedule = []
    current_day = combined_entries[0]["origin_date"]
    previous_dt = None

    for item in sorted(combined_entries, key=lambda x: parse_time(x["time"], x["origin_date"])):
        proposed_dt = parse_time(item["time"], current_day)
        if previous_dt and proposed_dt < previous_dt:
            current_day += timedelta(days=1)
            proposed_dt = parse_time(item["time"], current_day)
        item_dt = proposed_dt
        schedule.append({"start": item_dt, "title": item["title"], "desc": item["desc"]})
        previous_dt = item_dt

    for i, item in enumerate(schedule):
        start = item["start"]
        end = schedule[i + 1]["start"] if i + 1 < len(schedule) else start + timedelta(minutes=60)
        start_fmt = start.strftime("%Y%m%d%H%M%S +0300")
        end_fmt = end.strftime("%Y%m%d%H%M%S +0300")
        prog = ET.SubElement(tv, "programme", {"start": start_fmt, "stop": end_fmt, "channel": ch_id})
        ET.SubElement(prog, "title", {"lang": "bg"}).text = remove_quotes(html.unescape(item["title"]))
        desc_text = remove_quotes(html.unescape(item["desc"]))
        if desc_text:
            ET.SubElement(prog, "desc", {"lang": "bg"}).text = desc_text

rough_string = ET.tostring(tv, encoding="utf-8")
reparsed = minidom.parseString(rough_string)
pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

with open("/var/www/html/epg/tv_schedule.xml", "wb") as f:
    f.write(pretty_xml)

print("\n✅ tv_schedule.xml with broadcast-day rollover generated.")
