# tg-name-clock-docker

[中文文档](README.zh-CN.md)

## Overview
`tg-name-clock-docker` updates your Telegram first name with:
- Base name
- Current time (by timezone)
- Current weather from QWeather

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
- QWeather dedicated host and location

## Quick Start
1. Copy env template.
```bash
cp .env.example .env
```
2. Fill required values in `.env`.
3. Pull image.
```bash
docker pull ghcr.io/clavulin/telegram-name-clock-weather:latest
```
4. Run container.
```bash
docker run -d \
  --name tg-name-clock \
  --restart unless-stopped \
  --env-file .env \
  ghcr.io/clavulin/telegram-name-clock-weather:latest
```
5. Check logs.
```bash
docker logs -f tg-name-clock
```

## Build From Source (Optional)
```bash
docker compose up -d --build
docker compose logs -f
```

## Generate `TG_STRING_SESSION`
Install Telethon locally and run:

```python
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 123456
api_hash = "your_api_hash"

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("TG_STRING_SESSION=" + client.session.save())
```

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

## Security Notes
- Do not commit `.env`.
- Treat `TG_STRING_SESSION`, `QW_PRIVATE_KEY`, `QW_API_KEY`, and JWT as secrets.
- Rotate credentials immediately if leaked.

## License
MIT License. See [LICENSE](LICENSE).
