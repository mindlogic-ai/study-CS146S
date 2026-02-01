# Week 3 - Weather MCP Server

OpenWeatherMap API를 래핑한 MCP (Model Context Protocol) 서버입니다.

## Features

- **get_current_weather**: 도시의 현재 날씨 조회
- **get_forecast**: 도시의 5일 예보 조회

## Prerequisites

- Python 3.10+
- OpenWeatherMap API Key ([무료 발급](https://openweathermap.org/api))

## Setup

### 1. Install dependencies

```bash
cd week3/server
pip install -r requirements.txt
```

### 2. Configure environment variables

`.env` 파일 생성:

```bash
OPENWEATHER_API_KEY=your_api_key_here
```

### 3. Run the server (Local STDIO)

```bash
python main.py
```

## Claude Desktop Integration

`claude_desktop_config.json`에 추가:

```json
{
  "mcpServers": {
    "weather": {
      "command": "python",
      "args": ["path/to/week3/server/main.py"],
      "env": {
        "OPENWEATHER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

설정 파일 위치:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

## Tool Reference

### get_current_weather

현재 날씨를 조회합니다.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| city | string | Yes | 도시 이름 (예: "Seoul", "New York") |
| country_code | string | No | ISO 3166 국가 코드 (예: "KR", "US") |

**Example Input:**
```json
{
  "city": "Seoul",
  "country_code": "KR"
}
```

**Example Output:**
```
Current Weather for Seoul, KR:
- Condition: Clouds (overcast clouds)
- Temperature: 5.2°C (feels like 2.1°C)
- Humidity: 65%
- Wind: 3.5 m/s
- Pressure: 1020 hPa
```

### get_forecast

날씨 예보를 조회합니다.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| city | string | Yes | 도시 이름 |
| country_code | string | No | ISO 3166 국가 코드 |
| days | integer | No | 예보 일수 (1-5, 기본값: 3) |

**Example Input:**
```json
{
  "city": "Tokyo",
  "days": 2
}
```

**Example Output:**
```
Weather Forecast for Tokyo, JP:

📅 2025-02-01
  09:00 - 8.5°C, clear sky
  12:00 - 12.3°C, few clouds
  15:00 - 11.8°C, scattered clouds
  ...
```

## Error Handling

- **City not found**: 잘못된 도시 이름
- **Invalid API key**: API 키 오류
- **Rate limit exceeded**: API 호출 제한 초과
- **Timeout**: 요청 시간 초과 (10초)

## Project Structure

```
week3/
├── README.md
├── assignment.md
└── server/
    ├── main.py          # MCP 서버 메인 코드
    └── requirements.txt # 의존성
```
