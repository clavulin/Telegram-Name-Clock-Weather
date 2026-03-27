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


# --- Weather helpers (QWeather / HeWeather) ---
def qweather_emoji(icon_code: str) -> str:
    """
    基于和风 icon code 的粗粒度 emoji 映射（够用且稳定）。
    icon code 示例：白天晴 100、夜晚晴 150。 :contentReference[oaicite:2]{index=2}
    """
    try:
        code = int(icon_code)
    except Exception:
        return "☁️"

    # 晴（昼/夜）
    if code == 100:
        return "☀️"
    if code == 150:
        return "🌙"

    # 多云/阴（101-104；夜间多云/阴一般是 151-154）
    if 101 <= code <= 104 or 151 <= code <= 154:
        return "☁️"
    if code in (102, 103, 152, 153):
        return "🌤️"

    # 雾霾沙尘（500+）
    if 500 <= code <= 515:
        return "🌫️"

    # 雨（300-399）
    if 300 <= code <= 399:
        # 雷阵雨常见是 302/303（也可能有别的雷暴码）
        if code in (302, 303):
            return "⛈️"
        return "🌧️"

    # 雪/雨夹雪（400-499）
    if 400 <= code <= 499:
        return "🌨️"

    return "☁️"


def fetch_weather_qweather(timeout: float = 6.0) -> tuple[str, int]:
    """
    Returns: (emoji, temp_c_int)

    Endpoint: /v7/weather/now :contentReference[oaicite:3]{index=3}
    Auth: JWT (Authorization: Bearer ...) or API KEY. :contentReference[oaicite:4]{index=4}
    """
    host = os.environ["QW_HOST"].strip()          # 你的专属 API Host（不带 https://）
    location = os.environ["QW_LOCATION"].strip()  # 经度,纬度 或 LocationID

    jwt_token = os.environ.get("QW_JWT", "").strip()
    api_key = os.environ.get("QW_API_KEY", "").strip()
    if not jwt_token and not api_key:
        raise RuntimeError("Need QW_JWT or QW_API_KEY")

    url = f"https://{host}/v7/weather/now"
    params = {
        "location": location,
        "lang": os.environ.get("QW_LANG", "zh").strip(),
        "unit": os.environ.get("QW_UNIT", "m").strip(),  # m=metric
    }

    headers = {}
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    else:
        # API KEY 方式（header 更干净；也可用 params['key']=api_key）
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
    weather_refresh = float(os.environ.get("WEATHER_REFRESH_SECONDS", "1800"))  # 默认 30 分钟
    weather_enabled = os.environ.get("WEATHER_ENABLED", "1").strip() not in ("0", "false", "False")

    if not base_name:
        raise SystemExit("BASE_NAME is required (e.g. BASE_NAME='冰漫梦涯')")

    client = TelegramClient(StringSession(session_str), api_id, api_hash)

    last_target_hhmm = None
    last_set_name = None

    # Weather cache
    weather_text = ""  # e.g. "☁️25℃"
    next_weather_fetch_ts = 0.0

    with client:
        me = client.get_me()
        print(f"[INIT] Current Telegram first_name -> {me.first_name}")
        print(f"[INIT] TZ_NAME={tz_name} AHEAD_SECONDS={ahead_seconds} WEATHER_ENABLED={weather_enabled}")
        if weather_enabled:
            print(
                f"[INIT] QW_HOST={os.environ.get('QW_HOST')} "
                f"QW_LOCATION={os.environ.get('QW_LOCATION')} "
                f"WEATHER_REFRESH_SECONDS={weather_refresh}"
            )
        while True:
            try:
                # refresh weather if needed (cached)
                now_ts = time.time()
                if weather_enabled and now_ts >= next_weather_fetch_ts:
                    try:
                        emoji, temp_c = fetch_weather_qweather()
                        weather_text = f"{emoji}{to_fancy_number(str(temp_c))}°𝐂"
                        print(f"[WEATHER] Updated -> {weather_text}")
                    except Exception as e:
                        # 保留旧天气，不让它影响改名
                        print(f"[WEATHER_ERR] {type(e).__name__}: {e} (keeping last: '{weather_text}')")
                    next_weather_fetch_ts = now_ts + max(weather_refresh, 60.0)  # 最低 60 秒，防抖

                # time + schedule
                now_real = tz_now(tz_name)
                target_hhmm = compute_target_hhmm(now_real, ahead_seconds)

                if target_hhmm != last_target_hhmm:
                    plain_time = suffix_time_fmt.format(time=target_hhmm).strip()
                    time_part = to_fancy_number(plain_time)
                    # 拼接：冰漫梦涯 22:15 ☁️25℃ 
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
