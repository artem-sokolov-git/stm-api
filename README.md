# STM Montreal API — Portfolio Project

## Идея
REST API поверх открытых данных STM (Société de transport de Montréal), к которому можно подключить любой фронтенд — Telegram-бот, веб-карту, мобильное приложение.

## Источники данных

| Тип                      | URL                                                          | Доступ          |
| ------------------------ | ------------------------------------------------------------ | --------------- |
| GTFS Static (расписание) | `https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip` | Без регистрации |
| GTFS-RT TripUpdates      | `https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates`      | API-ключ        |
| GTFS-RT VehiclePositions | `https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions` | API-ключ        |

Регистрация: https://portail.developpeurs.stm.info/apihub

## Стек
- **FastAPI** — REST API
- **gtfs_kit** — парсинг GTFS Static (остановки, маршруты)
- **gtfs-realtime-bindings** — парсинг GTFS-RT protobuf
- **httpx** — async запросы к STM API
- **uv** — менеджер пакетов

## Структура проекта

```
stm-api/
├── app/
│   ├── main.py
│   ├── gtfs/
│   │   ├── static.py       # загрузка и парсинг GTFS ZIP
│   │   ├── realtime.py     # запросы к STM GTFS-RT
│   │   └── models.py       # dataclasses: Stop, Departure, Route
│   ├── api/
│   │   ├── stops.py        # GET /stops/nearby, GET /stops/{id}/departures
│   │   ├── routes.py       # GET /routes/{id}
│   │   └── vehicles.py     # GET /vehicles/positions
│   └── services/
│       ├── stops.py        # find_nearby_stops(), get_departures()
│       └── cache.py        # in-memory кэш
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## API Endpoints

```
GET /stops/nearby?lat=45.508&lon=-73.587&radius=500
GET /stops/{stop_id}/departures?limit=5
GET /vehicles/positions?route_id=69
GET /routes?search=69
```

## Структура GTFS-RT (TripUpdate)

```
FeedMessage
└── entity[]
      └── trip_update
            ├── trip
            │     ├── trip_id      # → trips.txt в GTFS Static
            │     ├── route_id     # номер маршрута ("69")
            │     └── schedule_relationship  # SCHEDULED | CANCELED
            ├── delay              # секунды (+опаздывает, -опережает)
            └── stop_time_update[]
                  ├── stop_id
                  ├── arrival.time    # Unix timestamp
                  ├── arrival.delay   # секунды
                  └── departure.time
```

## Telegram-бот (отдельный репозиторий)
- Клиент к stm-api через httpx
- Кнопка `request_location=True` → получаем lat/lon
- Запрос к `GET /stops/nearby` → список ближайших автобусов
- Live Location через `@router.edited_message(F.location)` для обновлений

## Алгоритм поиска ближайших остановок

```python
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2) -> float:
    """Возвращает расстояние в метрах"""
    R = 6_371_000
    φ1, φ2 = radians(lat1), radians(lat2)
    dφ, dλ = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dφ/2)**2 + cos(φ1) * cos(φ2) * sin(dλ/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))
```

## Референсы
- [nyctrains](https://github.com/arrismo/nyctrains) — аналогичная архитектура для MTA Нью-Йорка
- [gtfs_kit docs](https://github.com/mrcagney/gtfs_kit) — парсинг GTFS Static
- [morningcashee.com](https://www.morningcashee.com/blog/2024/06/13/getting-realtime-transit-data/) — туториал по STM GTFS-RT на Python

## Статус
- [ ] Зарегистрироваться на portail.developpeurs.stm.info
- [ ] Инициализировать проект (`uv init stm-api`)
- [ ] Парсинг GTFS Static (stops, routes, trips)
- [ ] Подключение GTFS-RT (tripUpdates)
- [ ] Endpoint `/stops/nearby`
- [ ] Endpoint `/stops/{id}/departures`
- [ ] Docker Compose
- [ ] README с архитектурной схемой
- [ ] Telegram-бот (отдельный репо)

## Конфигурация (pydantic-settings)

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    stm_api_key: str
    stm_trip_updates_url: str = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates"
    stm_vehicle_positions_url: str = "https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions"
    gtfs_static_url: str = "https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip"

    gtfs_cache_ttl: int = 3600        # секунды, как часто обновлять GTFS Static
    realtime_cache_ttl: int = 15      # секунды, как часто обновлять GTFS-RT
    nearby_stops_radius: int = 500    # метры по умолчанию

settings = Settings()
```

`.env.example`:
```dotenv
STM_API_KEY=your_api_key_here
# остальные поля опциональны — есть дефолты
```

Использование в приложении:
```python
from app.config import settings

headers = {"apikey": settings.stm_api_key}
response = await client.get(settings.stm_trip_updates_url, headers=headers)
```
