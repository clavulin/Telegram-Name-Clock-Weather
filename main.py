import os
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple

import requests
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors import FloodWaitError


# --- Time helpers ---
def tz_now(tz_name: str) -> datetime:
    from zoneinfo import ZoneInfo
    return datetime.now(ZoneInfo(tz_name))


def compute_target_hhmm(now_real: datetime, ahead_seconds: float) -> str:
    target_time = now_real + timedelta(seconds=ahead_seconds)
    return target_time.strftime("%H:%M")


def next_fire_time(now_real: datetime, ahead_seconds: float) -> datetime:
    target_time = now_real + timedelta(seconds=ahead_seconds)
    next_boundary = target_time.replace(second=0, microsecond=0) + timedelta(minutes=1)
    return next_boundary - timedelta(seconds=ahead_seconds)


def smart_sleep(seconds: float):
    if seconds > 0:
        time.sleep(seconds)


# --- Fancy number helpers ---
FANCY_DIGITS = {
    "0": "𝟎",
    "1": "𝟏",
    "2": "𝟐",
    "3": "𝟑",
    "4": "𝟒",
    "5": "𝟓",
    "6": "𝟔",
    "7": "𝟕",
    "8": "𝟖",
    "9": "𝟗",
}


def to_fancy_number(text: str) -> str:
    return "".join(FANCY_DIGITS.get(ch, ch) for ch in text)


# --- Telegram name helpers ---
def clamp_name(s: str, max_len: int = 64) -> str:
    return s[:max_len]


# --- Weather helpers (QWeather) ---
def qweather_emoji(icon_code: str) -> str:
    """
    Coarse-grained emoji mapping based on QWeather icon codes
    (practical and stable enough for everyday use).
    Example icon codes: clear during the day = 100, clear at night = 150.
    """
    try:
        code = int(icon_code)
    except Exception:
        return "☁️"

    # Clear (day / night)
    if code == 100:
        return "☀️"
    if code == 150:
        return "🌙"

    # Cloudy / overcast (101–104; nighttime cloudy / overcast is usually 151–154)
    if 101 <= code <= 104 or 151 <= code <= 154:
        return "☁️"
    if code in (102, 103, 152, 153):
        return "🌤️"

    # Fog / haze / dust / sand (500+)
    if 500 <= code <= 515:
        return "🌫️"

    # Rain (300–399)
    if 300 <= code <= 399:
        # Thunder showers are commonly 302/303
        if code in (302, 303):
            return "⛈️"
        return "🌧️"

    # Snow / sleet (400–499)
    if 400 <= code <= 499:
        return "🌨️"

    return "☁️"


def fetch_weather_qweather(timeout: float = 6.0) -> tuple[str, int]:
    """
    Returns: (emoji, temp_c_int)

    Endpoint: /v7/weather/now
    Auth: JWT (Authorization: Bearer ...) or API key
    """
    host = os.environ["QW_HOST"].strip()          # Dedicated API host (without https://)
    location = os.environ["QW_LOCATION"].strip()  # Longitude,latitude or LocationID

    jwt_token = os.environ.get("QW_JWT", "").strip()
    api_key = os.environ.get("QW_API_KEY", "").strip()
    if not jwt_token and not api_key:
        raise RuntimeError("Need QW_JWT or QW_API_KEY")

    url = f"https://{host}/v7/weather/now"
    params = {
        "location": location,
        "lang": os.environ.get("QW_LANG", "zh").strip(),
        "unit": os.environ.get("QW_UNIT", "m").strip(),  # m = metric
    }

    headers = {}
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    else:
        # API key method (cleaner in header; can also use params['key'] = api_key)
        headers["X-QW-Api-Key"] = api_key

    r = requests.get(url, params=params, headers=headers, timeout=timeout)
    r.raise_for_status()
    data = r.json()

    if data.get("code") != "200":
        raise RuntimeError(f"QWeather error code={data.get('code')}")

    now = data.get("now") or {}
    temp = now.get("temp")
    icon = now.get("icon")
    if temp is None or icon is None:
        raise RuntimeError("QWeather response missing now.temp/now.icon")

    emoji = qweather_emoji(str(icon))
    return emoji, int(round(float(temp)))


def main():
    # Telegram auth
    api_id = int(os.environ["TG_API_ID"])
    api_hash = os.environ["TG_API_HASH"]
    session_str = os.environ["TG_STRING_SESSION"]

    # Name format
    base_name = os.environ.get("BASE_NAME", "").strip()
    tz_name = os.environ.get("TZ_NAME", "Australia/Sydney").strip()
    suffix_time_fmt = os.environ.get("TIME_FORMAT", "{time}").strip()  # default "{time}"

    # Scheduling
    ahead_seconds = float(os.environ.get("AHEAD_SECONDS", "0"))
    guard_seconds = float(os.environ.get("GUARD_SECONDS", "0.15"))

    # Weather config
    weather_refresh = float(os.environ.get("WEATHER_REFRESH_SECONDS", "1800"))  # default: 30 minutes
    weather_enabled = os.environ.get("WEATHER_ENABLED", "1").strip() not in ("0", "false", "False")

    if not base_name:
        raise SystemExit("BASE_NAME is required (e.g. BASE_NAME='YourName')")

    client = TelegramClient(StringSession(session_str), api_id, api_hash)

    last_target_hhmm = None
    last_set_name = None

    # Weather cache
    weather_text = ""  # e.g. "☁️25°C"
    next_weather_fetch_ts = 0.0

    with client:
        me = client.get_me()
        print(f"[INIT] Current Telegram first_name -> {me.first_name}")
        print(f"[INIT] TZ_NAME={tz_name} AHEAD_SECONDS={ahead_seconds} WEATHER_ENABLED={weather_enabled}")
        if weather_enabled:
            print(
                f"[INIT] QW_HOST=[REDACTED_HOST] "
                f"QW_LOCATION=[REDACTED_LOCATION] "
                f"WEATHER_REFRESH_SECONDS={weather_refresh}"
            )

        while True:
            try:
                # Refresh weather if needed (cached)
                now_ts = time.time()
                if weather_enabled and now_ts >= next_weather_fetch_ts:
                    try:
                        emoji, temp_c = fetch_weather_qweather()
                        weather_text = f"{emoji}{to_fancy_number(str(temp_c))}°𝐂"
                        print(f"[WEATHER] Updated -> {weather_text}")
                    except Exception as e:
                        # Keep the previous weather value so it does not affect name updates
                        print(f"[WEATHER_ERR] {type(e).__name__}: {e} (keeping last: '{weather_text}')")
                    next_weather_fetch_ts = now_ts + max(weather_refresh, 60.0)  # minimum 60s to avoid excessive refresh

                # Time + schedule
                now_real = tz_now(tz_name)
                target_hhmm = compute_target_hhmm(now_real, ahead_seconds)

                if target_hhmm != last_target_hhmm:
                    plain_time = suffix_time_fmt.format(time=target_hhmm).strip()
                    time_part = to_fancy_number(plain_time)

                    # Example: YourName 22:15 ☁️25°C
                    name_parts = [base_name, time_part]

                    if weather_enabled and weather_text:
                        name_parts.append(weather_text)

                    new_name = clamp_name(" ".join(name_parts))

                    if new_name != last_set_name:
                        print(f"[TRY] Setting name -> {new_name}")
                        client(UpdateProfileRequest(first_name=new_name))
                        me = client.get_me()
                        print(f"[CONFIRM] Telegram now shows -> {me.first_name}")
                        last_set_name = me.first_name

                    last_target_hhmm = target_hhmm

                fire_time = next_fire_time(now_real, ahead_seconds)
                sleep_s = (fire_time - tz_now(tz_name)).total_seconds() - guard_seconds
                smart_sleep(sleep_s)

                while tz_now(tz_name) < fire_time:
                    smart_sleep(0.005)

            except FloodWaitError as e:
                wait_s = int(getattr(e, "seconds", 60))
                print(f"[FLOOD] Need to wait {wait_s}s")
                smart_sleep(wait_s + 1)
            except Exception as e:
                print(f"[ERR] {type(e).__name__}: {e}")
                smart_sleep(5)


if __name__ == "__main__":
    main()
