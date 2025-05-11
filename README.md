📺 XMLTV EPG Generator

This script scrapes TV program data from multiple Bulgarian EPG sources and generates an XMLTV-compliant file (tv_schedule.xml) with accurate broadcast-day segmentation.
✅ Features

    Combines data from multiple sources:

        dir.bg

        dnevnik.bg

        start.bg

        https://github.com/harrygg/EPG

    Supports fallback mechanism: if a channel's preferred source fails, it tries others.

    Handles 3 consecutive days (today, tomorrow, day after tomorrow).

    Automatically corrects start/end times and avoids overlapping.

    Strips special quote characters and encodes clean UTF-8 output.

📦 Output

Generates:

/var/www/html/epg/tv_schedule.xml

🧠 Channel Configuration (channels.json)

Supports structured fallback for each channel:

```json

{
  "tv_channels": [
    {
      "xml": "bTV",
      "sources": [
        { "id": "12", "name": "bTV", "source": "dir.bg" },
        { "id": "116", "name": "btv", "source": "dnevnik.bg" },
        { "id": "123", "name": "bTV", "source": "start.bg" },
        { "id": "", "name": "btv.bg", "source": "harrygg" }
      ]
    }
  ]
}

```

    xml: ID used in <channel id="..."> and icon naming.

    sources: List of sources to try, in fallback order.

⚙️ Source URL Formats

    dir.bg: https://tv.dir.bg/tv_channel.php?id={id}&dd={dd.mm}

    dnevnik.bg: https://www.dnevnik.bg/sled5/tv/{id}_{name}/{yyyymmdd}/

    start.bg: https://www.start.bg/lenta/tv-programa//tv/show/channel/{id}/{yyyy-mm-dd}/0

## Requirements

* Python 3.x
* `requests` and `beautifulsoup4`

Install dependencies:

```bash
pip install requests beautifulsoup4
```
```bash
python3 tvxml.py
```
