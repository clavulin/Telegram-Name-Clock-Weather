# Telegram-Name-Clock-Weather

一个基于 Telethon 的 Telegram 昵称时钟脚本，支持在昵称里显示：

- 基础昵称（`BASE_NAME`）
- 当前时间（按指定时区）
- 实时天气（QWeather）

项目通过 Docker 运行，配置集中在 `.env`。

## 1. 运行前准备

你需要先准备：

1. Telegram `API_ID` 和 `API_HASH`
2. 一个可用的 `TG_STRING_SESSION`
3. QWeather 的专属 Host（`QW_HOST`）和位置（`QW_LOCATION`）
4. 天气鉴权二选一：
   - `QW_JWT`（推荐）
   - `QW_API_KEY`

## 2. 生成 Telethon StringSession

先安装依赖：

```bash
pip install telethon==1.35.0
```

新建一个 `gen_session.py`：

```python
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 123456
api_hash = "your_api_hash"

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("TG_STRING_SESSION=" + client.session.save())
```

运行：

```bash
python gen_session.py
```

按提示输入手机号、验证码、二步密码（如果开启）。把输出的 `TG_STRING_SESSION=...` 填到 `.env`。

## 3. 配置 .env

最少需要这些变量（与代码实际读取一致）：

```env
TG_API_ID=
TG_API_HASH=
TG_STRING_SESSION=

BASE_NAME=你的名字
TZ_NAME=China/Shanghai
TIME_FORMAT={time}
AHEAD_SECONDS=0.2
GUARD_SECONDS=0.2

WEATHER_ENABLED=1
WEATHER_REFRESH_SECONDS=1800

QW_HOST=your-host.re.qweatherapi.com
QW_LOCATION=121.47,31.23

# 二选一（推荐 JWT）
QW_JWT=
# QW_API_KEY=

QW_LANG=zh
QW_UNIT=m
```

说明：

- `TIME_FORMAT` 支持 `{time}` 占位符，例如 `{time}`、`[{time}]`
- `QW_LOCATION` 可用 `经度,纬度` 或 LocationID
- 不要同时使用 `QW_JWT` 和 `QW_API_KEY`

## 4. Docker 启动

构建并后台运行：

```bash
docker compose up -d --build
```

查看日志：

```bash
docker compose logs -f
```

停止：

```bash
docker compose down
```

## 5. 常见问题

1. `Need QW_JWT or QW_API_KEY`
   - 说明天气鉴权未配置，补 `QW_JWT` 或 `QW_API_KEY`
2. QWeather 返回 401
   - 检查 `QW_HOST` 是否是控制台分配的专属 Host
   - 检查 JWT 的 `kid/sub/签名` 是否对应同一项目与密钥
3. Telegram 改名失败或出现 FloodWait
   - 这是 Telegram 频率限制，等待后会自动恢复
