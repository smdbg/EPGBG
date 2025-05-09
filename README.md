# XMLTV EPG Generator

This script generates a multi-day XMLTV-compliant Electronic Program Guide (EPG) from multiple sources such as `dir.bg` and `dnevnik.bg`. It supports multiple channels and dynamically adjusts for broadcast days that span past midnight.

## Features

* Parses TV schedules from:

  * `dir.bg`: using `<ul id="events">` format
  * `dnevnik.bg`: using `<table class="expanded">` format
* Supports 3-day broadcast EPG (today, tomorrow, and the day after)
* Outputs valid `tv_schedule.xml` with proper `<programme>`, `<title>`, and `<desc>` tags
* Handles time rollover after midnight
* Skips empty schedules to avoid errors
* Displays a terminal progress bar during generation

## Requirements

* Python 3.x
* `requests` and `beautifulsoup4`

Install dependencies:

```bash
pip install requests beautifulsoup4
```

## Setup

1. Create a `channels.json` file:

```json
{
  "tv_channels": [
    {"id": "12", "name": "btv", "source": "dir.bg"},
    {"id": "28", "name": "nova", "source": "dir.bg"},
    {"id": "93", "name": "bnt1", "source": "dnevnik.bg"}
  ]
}
```

*Make sure `name` matches the lowercase slug used in the URL for `dnevnik.bg`.*

2. Run the script:

```bash
python3 generate_xmltv.py
```
