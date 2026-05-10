# Telegram Name Clock Weather

[English README](README.md)

## 项目简介
`Telegram Name Clock Weather` 会持续更新 Telegram 的 first name，内容包括：
- 基础昵称
- 当前时间（按时区）
- [QWeather](https://dev.qweather.com/) 实时天气

项目通过 Docker 持续运行。

## 功能
- 按分钟更新昵称，支持调度提前量与安全余量
- 支持 QWeather 动态 JWT（推荐）
- 时间和温度可分别选择多种 Unicode 数字/字母样式
- 兼容静态 JWT 或 API Key
- 通过 `.env` 简单配置
- 提供 GHCR 预构建镜像

效果展示：

    Alice 𝟏𝟑:𝟓𝟏 ☀️𝟐𝟎°𝐂
    
## 运行要求
- Docker
- Telegram `API_ID`、`API_HASH`、`TG_STRING_SESSION`
- [QWeather](https://dev.qweather.com/) 鉴权、专属 host 与位置参数

## 快速开始（Docker Compose + GHCR 镜像）
1. 克隆到本地。
```bash
git clone https://github.com/clavulin/telegram-name-clock-weather.git
cd telegram-name-clock-weather
```
2. 复制环境变量模板。
```bash
cp .env.example .env
```
3. 编辑 `.env`，填入必填项。
4. 拉取并启动。
```bash
docker compose pull
docker compose up -d
```
5. 查看日志。
```bash
docker compose logs -f
```

## 源码构建（可选）
1. 克隆到本地。
```bash
git clone https://github.com/clavulin/telegram-name-clock-weather.git
cd telegram-name-clock-weather
```
2. 复制环境变量模板。
```bash
cp .env.example .env
```
3. 编辑 `.env`，填入必填项。
4. 本地构建并启动容器。
```bash
docker build -t telegram-name-clock-weather:local .
docker run -d \
  --name telegram-name-clock-weather \
  --restart unless-stopped \
  --env-file .env \
  telegram-name-clock-weather:local
```
5. 查看日志。
```bash
docker logs -f telegram-name-clock-weather
```

## 生成 `TG_STRING_SESSION`
本地安装 Telethon 后运行以下脚本：

```python
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = 123456
api_hash = "your_api_hash"

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("TG_STRING_SESSION=" + client.session.save())
```

## 环境变量说明
当前代码实际读取的主要变量如下：

| 变量 | 是否必填 | 说明 |
|---|---|---|
| `TG_API_ID` | 是 | Telegram API ID |
| `TG_API_HASH` | 是 | Telegram API Hash |
| `TG_STRING_SESSION` | 是 | Telethon 会话串 |
| `BASE_NAME` | 是 | 昵称基础文本 |
| `TZ_NAME` | 否 | 时区，默认 `Australia/Sydney` |
| `TIME_FORMAT` | 否 | 时间格式模板，默认 `{time}` |
| `TIME_STYLE` | 否 | 时间样式：`normal`、`bold`（兼容别名 `fancy`）、`italic`、`bold_italic`、`script`、`bold_script`、`fraktur`、`bold_fraktur`、`double_struck`、`sans`、`sans_italic`、`sans_bold`、`sans_bold_italic`、`monospace`；也接受 `sans-serif-bold`、`sans serif bold` 这类连字符/空格别名；不含数字字形的样式会自动保留普通数字 |
| `TEMP_STYLE` | 否 | 温度样式：同 `TIME_STYLE`，作用于数字和 `C`，默认 `fancy` |
| `AHEAD_SECONDS` | 否 | 提前量（秒） |
| `GUARD_SECONDS` | 否 | 调度安全余量（秒） |
| `WEATHER_ENABLED` | 否 | 天气开关，默认 `1` |
| `WEATHER_REFRESH_SECONDS` | 否 | 天气刷新间隔 |
| `QW_HOST` | 开天气时必填 | QWeather 专属 API Host |
| `QW_LOCATION` | 开天气时必填 | `经度,纬度` 或 LocationID |
| `QW_LANG` | 否 | 天气语言，默认 `zh` |
| `QW_UNIT` | 否 | 计量单位，默认 `m` |

QWeather 鉴权三选一：

方案 A（推荐，动态 JWT）：
- `QW_PROJECT_ID`
- `QW_KEY_ID`
- `QW_PRIVATE_KEY`（PEM 文本或 base64 DER）
- `QW_JWT_TTL_SECONDS`（可选，默认 `900`）

方案 B：
- `QW_JWT`（静态 token）

方案 C：
- `QW_API_KEY`

## 样式预览

使用示例名 `Alice 13:51 ☀️20°C` 的完整预览：

```text
normal            | Alice 13:51 ☀️20°C
bold              | Alice 𝟏𝟑:𝟓𝟏 ☀️𝟐𝟎°𝐂
italic            | Alice 13:51 ☀️20°𝐶
bold_italic       | Alice 13:51 ☀️20°𝑪
script            | Alice 13:51 ☀️20°𝒞
bold_script       | Alice 13:51 ☀️20°𝓒
fraktur           | Alice 13:51 ☀️20°ℭ
bold_fraktur      | Alice 13:51 ☀️20°𝕮
double_struck     | Alice 𝟙𝟛:𝟝𝟙 ☀️𝟚𝟘°ℂ
sans              | Alice 𝟣𝟥:𝟧𝟣 ☀️𝟤𝟢°𝖢
sans_italic       | Alice 13:51 ☀️20°𝘊
sans_bold         | Alice 𝟭𝟯:𝟱𝟭 ☀️𝟮𝟬°𝗖
sans_bold_italic  | Alice 13:51 ☀️20°𝘾
monospace         | Alice 𝟷𝟹:𝟻𝟷 ☀️𝟸𝟶°𝙲
```

说明：
- `fancy` 是 `bold` 的兼容别名。
- 某些 Unicode 样式没有数字字形，因此时间和温度数字会保持普通样式，只替换 `C`。

## 常见问题
- `Need dynamic JWT envs ... or QW_JWT, or QW_API_KEY`
  - 未配置鉴权参数，请补全动态 JWT 变量，或改用静态 JWT/API Key。
- QWeather 返回 `401`
  - 检查 `QW_HOST`、项目ID/密钥ID、私钥与 JWT 有效期。
- Telegram 出现 FloodWait
  - 触发频率限制，等待后重试。
