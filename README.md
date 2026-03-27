# STM Montreal API — Portfolio Project

## Идея
REST API поверх открытых данных STM (Société de transport de Montréal), к которому можно подключить любой фронтенд — Telegram-бот, веб-карту, мобильное приложение.

## Источники данных

| Тип                      | URL                                                          | Доступ          |
| ------------------------ | ------------------------------------------------------------ | --------------- |
| GTFS Static (расписание) | `https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip` | Без регистрации |
| GTFS-RT TripUpdates      | `https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates`      | API-ключ        |
| GTFS-RT VehiclePositions | `https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions` | API-ключ        |
| Service Status           | `https://api.stm.info/pub/od/i3/v2/messages/etatservice`     | API-ключ        |

Регистрация: https://portail.developpeurs.stm.info/apihub

## Стек

- **FastAPI** — REST API
- **Granian** — ASGI-сервер (замена uvicorn)
- **httpx** — HTTP-клиент для запросов к STM API
- **pydantic-settings** — конфигурация через переменные окружения
- **uv** — менеджер пакетов
- **pytest** — интеграционные тесты
- **ruff** — линтер и форматтер
- **ty** — проверка типов
- **Docker / Docker Compose** — контейнеризация

## Структура проекта

```
stm-api/
├── core/
│   ├── __init__.py
│   ├── config.py           # pydantic-settings: токен, URL endpoints
│   ├── client.py           # httpx.AsyncClient factory с apikey заголовком
│   ├── main.py             # FastAPI app
│   ├── filters/
│   │   └── vehicles.py     # VehicleFilter dataclass (query params)
│   ├── models/
│   │   └── vehicles.py     # VehiclePosition Pydantic model
│   ├── routers/
│   │   ├── health.py       # GET /ping
│   │   └── vehicles.py     # GET /vehicles
│   └── services/
│       └── vehicles.py     # fetch_vehicles(): GTFS-RT → VehiclePosition
├── tests/
│   ├── conftest.py         # pytest fixtures (httpx.Client с apikey)
│   └── test_stm_status.py  # интеграционные тесты STM API
├── .env                    # переменные окружения (TOKEN)
├── .pre-commit-config.yaml # ruff + стандартные хуки
├── docker-compose.yaml
├── Dockerfile
├── Makefile
├── pyproject.toml
└── uv.lock
```

## Конфигурация

Настройки читаются из `.env` через `pydantic-settings`:

```python
# core/config.py
class Settings(ApplicationSettings, GTFSRealtimeSettings, STMServiceStatusSettings):
    pass

settings = Settings()
```

`.env`:
```dotenv
TOKEN=your_api_key_here
```

Переменная `TOKEN` используется как `apikey` в заголовках запросов к STM API.

## API Endpoints

### `GET /ping`
Healthcheck.

```json
{"status": "ok"}
```

### `GET /vehicles`
Реальные позиции всех активных транспортных средств STM из GTFS-RT фида.

**Query params:**

| Параметр       | Тип  | Описание                          |
| -------------- | ---- | --------------------------------- |
| `route_id`     | str  | Фильтр по маршруту (например, `69`) |
| `direction_id` | int  | Фильтр по направлению (`0` или `1`) |

**Пример ответа:**

```json
[
  {
    "id": "string",
    "route_id": "69",
    "direction_id": 0,
    "trip_id": "string",
    "latitude": 45.508,
    "longitude": -73.587,
    "bearing": 180.0,
    "speed": 10.5,
    "current_status": 2,
    "stop_id": "string",
    "occupancy_status": 1,
    "timestamp": 1711500000
  }
]
```

## Архитектура

Поток данных для `/vehicles`:

```
router → service → STM GTFS-RT (protobuf) → VehiclePosition models → фильтрация
```

- **Routers** (`core/routers/`) — HTTP-слой, принимают query params через `Depends()`
- **Services** (`core/services/`) — бизнес-логика, async HTTP-запросы к STM API
- **Models** (`core/models/`) — Pydantic-модели для ответов
- **Filters** (`core/filters/`) — dataclass-зависимости для query params
- **Client** (`core/client.py`) — `stm_client()` возвращает `httpx.AsyncClient` с pre-injected `apikey`

## Доступные команды (Makefile)

```
make run       # Собрать и запустить контейнер
make down      # Остановить контейнер
make logs      # Логи контейнера
make rebuild   # Пересобрать проект с нуля
make check     # ruff lint + format check + ty check
make tests     # Запустить pytest
```

## Запуск

```bash
# Локально
uv run granian --interface asgi --host 0.0.0.0 --port 8000 core.main:app

# Docker
make run
```

## Тесты

Интеграционные тесты — обращаются к реальному STM API. Требуется валидный `.env` с `TOKEN`.

```bash
make tests
# или отдельный тест:
uv run pytest tests/test_stm_status.py::test_vehicle_positions
```

## Деплой

Push в `main` → GitHub Actions → сборка Docker-образа → push в GitHub Container Registry (`ghcr.io`).
Образ тегируется как `latest` и `sha-<commit>`.

## Статус

- [x] Зарегистрироваться на portail.developpeurs.stm.info
- [x] Инициализировать проект (`uv init stm-api`)
- [x] Конфигурация через pydantic-settings
- [x] Docker / Docker Compose с healthcheck
- [x] HTTP-клиент (`httpx.AsyncClient`) с pre-injected apikey
- [x] Интеграционные тесты GTFS-RT и Service Status
- [x] `GET /vehicles` с фильтрацией по `route_id` и `direction_id`
- [x] CI/CD: GitHub Actions → GHCR
- [ ] Парсинг GTFS Static (stops, routes, trips)
- [ ] Endpoint `/stops/nearby`
- [ ] Endpoint `/stops/{id}/departures`
- [ ] Telegram-бот (отдельный репо)

## Референсы

- [nyctrains](https://github.com/arrismo/nyctrains) — аналогичная архитектура для MTA Нью-Йорка
- [gtfs_kit docs](https://github.com/mrcagney/gtfs_kit) — парсинг GTFS Static
- [morningcashee.com](https://www.morningcashee.com/blog/2024/06/13/getting-realtime-transit-data/) — туториал по STM GTFS-RT на Python
