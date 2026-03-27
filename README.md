# Telegram Name Clock Weather

A lightweight Python tool that automatically updates your **Telegram
profile name** to display:

-   ⏰ current time
-   🌤 weather information
-   👤 your custom base name

It runs continuously and updates your Telegram name periodically using
**Telethon**.

------------------------------------------------------------------------

# Features

-   Automatic Telegram name updates
-   Real-time clock display
-   Weather integration via **[QWeather](https://dev.qweather.com/en/)**
-   Timezone support
-   Minimal resource usage
-   Easy deployment with **Docker**

Example name format:

    Alice 14:32 ☀️25°C

------------------------------------------------------------------------

# Quick Start (Docker -- Recommended)

Pull the prebuilt image:

``` bash
docker pull ghcr.io/clavulin/telegram-name-clock-weather:latest
```

Create a `.env` file:

``` env
# Telegram API credentials
TG_API_ID=123456
TG_API_HASH=abcdef123456abcdef123456abcdef12

# Important: Pre-generated Telethon StringSession
TG_STRING_SESSION=

# Base name shown before the clock
BASE_NAME=Alice

# Timezone used for the clock
TZ_NAME=Europe/London

# Update interval in seconds
# Recommended >= 60 (too frequent updates may trigger Telegram FloodWait)
INTERVAL_SECONDS=60

# Suffix format (default: {time})
SUFFIX_FORMAT={time}

# Polling frequency (seconds)
# This only checks time changes and does NOT update the name every second
POLL_SECONDS=1

# Jump ahead to the next minute slightly earlier
AHEAD_SECONDS=0

# Scheduler safety margin
# Values between 0.1 and 0.5 are usually safe
GUARD_SECONDS=0.2

# Enable weather display
WEATHER_ENABLED=1

# Weather refresh interval (seconds)
# Default: 1800 seconds (30 minutes)
WEATHER_REFRESH_SECONDS=1800

# QWeather API host (without https://)
QW_HOST=your-host.qweather.com

# Weather location (longitude,latitude) or LocationID
# Example: London
QW_LOCATION=0.1276,51.5072

# Authentication (choose ONE)
# Recommended: JWT
QW_JWT=

# Or API key
# QW_API_KEY=your_api_key_here

# Optional settings
QW_LANG=en
QW_UNIT=m
```

Run the container:

``` bash
docker run -d \
  --name telegram-name-clock-weather \
  --env-file .env \
  --restart unless-stopped \
  ghcr.io/clavulin/telegram-name-clock-weather:latest
```

------------------------------------------------------------------------

# Docker Compose

``` yaml
services:
  telegram-name-clock-weather:
    image: ghcr.io/clavulin/telegram-name-clock-weather:latest
    container_name: telegram-name-clock-weather
    restart: unless-stopped
    env_file:
      - .env
```

Start:

``` bash
docker compose up -d
```

------------------------------------------------------------------------

# Getting Telegram API Credentials

1.  Go to https://my.telegram.org
2.  Login with your phone number
3.  Open **API development tools**
4.  Create an application

You will receive:

    api_id
    api_hash

------------------------------------------------------------------------

# Getting Weather API

This project uses QWeather for weather data.

To get your weather API key, visit the [QWeather Developer Platform](https://dev.qweather.com/en/).

------------------------------------------------------------------------

# Generate Telethon String Session

Install Telethon locally:

``` bash
pip install telethon
```

Run:

``` python
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 123456
api_hash = "your_api_hash"

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print(client.session.save())
```

Copy the printed session string into:

    TG_STRING_SESSION

------------------------------------------------------------------------

# Build Image Manually

Clone repository:

``` bash
git clone https://github.com/clavulin/Telegram-Name-Clock-Weather.git
cd Telegram-Name-Clock-Weather
```

Build image:

``` bash
docker build -t telegram-name-clock-weather .
```

Run:

``` bash
docker run --env-file .env telegram-name-clock-weather
```

------------------------------------------------------------------------

# Development

Run locally without Docker:

``` bash
pip install -r requirements.txt
python main.py
```

------------------------------------------------------------------------

# Project Structure

    Telegram-Name-Clock-Weather
    ├── Dockerfile
    ├── main.py
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

# License

MIT License

------------------------------------------------------------------------

# Contributing

Pull requests are welcome.

If you have ideas for improvements (new features, bug fixes, better
formatting), feel free to open an issue or PR.

------------------------------------------------------------------------

# Acknowledgements

-   Telegram API
-   Telethon
-   QWeather
