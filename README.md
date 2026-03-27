# Telegram Name Clock Weather

[中文文档](README.zh-CN.md)

## Overview
`Telegram Name Clock Weather` updates your Telegram first name with:
- Base name
- Current time (by timezone)
- Current weather from [QWeather](https://dev.qweather.com)

It runs continuously in Docker.

## Features
- Minute-level name update with configurable schedule offsets
- QWeather support with dynamic JWT generation (recommended)
- Fallback auth support: static JWT or API key
- Simple `.env`-driven configuration
- Prebuilt Docker image on GHCR

## Requirements
- Docker + Docker Compose
- Telegram `API_ID`, `API_HASH`, and `TG_STRING_SESSION`
- [QWeather](https://dev.qweather.com) auth, dedicated host and location

## Quick Start (GHCR Image via Docker Compose)
1. Clone to local.
```bash
git clone https://github.com/clavulin/telegram-name-clock-weather.git
cd telegram-name-clock-weather
```
2. Copy env template.
```bash
cp .env.example .env
```
3. Fill required values in `.env`.
4. Pull and start.
```bash
docker compose pull
docker compose up -d
```
5. Check logs.
```bash
docker compose logs -f
```

## Build From Source (Optional)
1. Clone to local.
```bash
git clone https://github.com/clavulin/telegram-name-clock-weather.git
cd telegram-name-clock-weather
```
2. Copy env template.
```bash
cp .env.example .env
```
3. Fill required values in `.env`.
4. Build local image and run.
```bash
docker build -t telegram-name-clock-weather:local .
docker run -d \
  --name telegram-name-clock-weather \
  --restart unless-stopped \
  --env-file .env \
  telegram-name-clock-weather:local
```
5. Check logs.
```bash
docker logs -f telegram-name-clock-weather
```

## Generate `TG_STRING_SESSION`
```bash
docker run -it --rm python:3.11 bash -c "
pip install telethon && \
python - << 'EOF'
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = int(input('API_ID: '))
api_hash = input('API_HASH: ')

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print('TG_STRING_SESSION=' + client.session.save())
EOF"
```

Steps:
1.	Run the command above
2.	Enter your API_ID
3.	Enter your API_HASH
4.	Enter your Telegram phone number
5.	Enter the verification code

You will get:
```bash
TG_STRING_SESSION=xxxxxxxxxxxxxxxxxxxxxxxx
```
Copy it into your .env file.

## Environment Variables
Required app variables used by current code:

| Variable | Required | Description |
|---|---|---|
| `TG_API_ID` | Yes | Telegram API ID |
| `TG_API_HASH` | Yes | Telegram API hash |
| `TG_STRING_SESSION` | Yes | Telethon string session |
| `BASE_NAME` | Yes | Base display name |
| `TZ_NAME` | No | Timezone, default `Australia/Sydney` |
| `TIME_FORMAT` | No | Time template, default `{time}` |
| `AHEAD_SECONDS` | No | Update lead offset |
| `GUARD_SECONDS` | No | Schedule guard offset |
| `WEATHER_ENABLED` | No | Weather switch, default `1` |
| `WEATHER_REFRESH_SECONDS` | No | Weather refresh interval |
| `QW_HOST` | Yes (if weather on) | QWeather dedicated API host |
| `QW_LOCATION` | Yes (if weather on) | `lon,lat` or LocationID |
| `QW_LANG` | No | Weather language, default `zh` |
| `QW_UNIT` | No | Weather unit, default `m` |

QWeather auth (choose one path):

Path A (recommended, dynamic JWT):
- `QW_PROJECT_ID`
- `QW_KEY_ID`
- `QW_PRIVATE_KEY` (PEM text or base64 DER)
- `QW_JWT_TTL_SECONDS` (optional, default `900`)

Path B:
- `QW_JWT` (static token)

Path C:
- `QW_API_KEY`

## Troubleshooting
- `Need dynamic JWT envs ... or QW_JWT, or QW_API_KEY`
  - Configure dynamic JWT variables, or set static JWT/API key.
- QWeather `401 Unauthorized`
  - Verify `QW_HOST`, key/project IDs, private key, and token TTL.
- Telegram FloodWait
  - Telegram rate-limited the account. Wait and retry.
