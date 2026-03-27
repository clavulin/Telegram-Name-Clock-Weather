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
-   Weather integration via **QWeather**
-   Timezone support
-   Minimal resource usage
-   Easy deployment with **Docker**

Example name format:

    Alice 14:32 ☀️ 25°C

------------------------------------------------------------------------

# Quick Start (Docker -- Recommended)

Pull the prebuilt image:

``` bash
docker pull ghcr.io/clavulin/telegram-name-clock-weather:latest
```

Create a `.env` file:

``` env
TG_API_ID=123456
TG_API_HASH=xxxxxxxxxxxxxxxx
TG_STRING_SESSION=xxxxxxxxxxxxxxxx

BASE_NAME=Alice
TZ_NAME=Australia/Sydney

QW_HOST=your-host.qweather.com
QW_LOCATION=151.21,-33.87
QW_JWT=xxxxxxxxxxxxxxxx
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

# Environment Variables

| Variable | Required | Example | Description |
|---|---|---|---|
| `TG_API_ID` | Yes | `123456` | Telegram API ID |
| `TG_API_HASH` | Yes | `abcd1234...` | Telegram API Hash |
| `TG_STRING_SESSION` | Yes | `1AQA...` | Telethon string session used for authentication |
| `BASE_NAME` | Yes | `Alice` | Base name displayed before the time |
| `TZ_NAME` | Yes | `Australia/Sydney` | Timezone used for the clock |
| `QW_HOST` | Yes | `api.qweather.com` | QWeather API host |
| `QW_LOCATION` | Yes | `151.21,-33.87` | Weather location in `longitude,latitude` |
| `QW_JWT` | Yes | `eyJhbGciOiJIUzI1Ni...` | QWeather API JWT token |

# Getting Telegram API Credentials

1.  Go to https://my.telegram.org
2.  Login with your phone number
3.  Open **API development tools**
4.  Create an application

You will receive:

    api_id
    api_hash

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
