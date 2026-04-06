# Transit API — Portfolio Project

REST API поверх открытых данных STM (Société de transport de Montréal). Можно подключить к любому фронтенду — Telegram-бот, веб-карту, мобильное приложение.

## Стек

- **FastAPI** — REST API
- **Granian** — ASGI-сервер (Rust-based, замена uvicorn)
- **httpx** — async HTTP-клиент для запросов к STM API
- **gtfs-realtime-bindings** — парсинг Protocol Buffer GTFS-RT
- **SQLAlchemy + aiosqlite** — хранение и запросы к GTFS Static (SQLite)
- **pydantic-settings** — конфигурация через переменные окружения
- **uv** — менеджер пакетов
- **pytest** — интеграционные тесты
- **ruff** — линтер и форматтер
- **ty** — проверка типов
- **Docker / Docker Compose** — контейнеризация

## Источники данных

| Тип                      | Endpoint                                                         | Доступ   |
| ------------------------ | ---------------------------------------------------------------- | -------- |
| GTFS-RT VehiclePositions | `https://api.stm.info/pub/od/gtfs-rt/ic/v2/vehiclePositions`    | API-ключ |
| GTFS-RT TripUpdates      | `https://api.stm.info/pub/od/gtfs-rt/ic/v2/tripUpdates`         | API-ключ |
| Service Status           | `https://api.stm.info/pub/od/i3/v2/messages/etatservice`        | API-ключ |
| GTFS Static (zip)        | `https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip`    | Открытый |

Регистрация: https://portail.developpeurs.stm.info/apihub

## Архитектура

```
# Реальное время
router → service → STM GTFS-RT (protobuf) → Pydantic models → фильтрация

# Статика
router → service → SQLite (SQLAlchemy async) → Pydantic models
```

Пакет `core/` организован по слоям:

- **Routers** (`core/routers/`) — HTTP-слой, query params через `Depends()`
- **Services** (`core/services/`) — бизнес-логика, async HTTP-запросы к STM API
- **Models** (`core/models/`) — Pydantic-модели ответов
- **Filters** (`core/filters/`) — dataclass-зависимости для query params
- **Client** (`core/client.py`) — `auth_client()` возвращает `httpx.AsyncClient` с pre-injected `apikey`
- **Static** (`core/static/stm/`) — `StaticDB`: при старте загружает GTFS zip и сохраняет в SQLite; обновляется если БД старше `GTFS_MAX_AGE_DAYS` (по умолчанию 7 дней)
- **Config** (`core/config.py`) — `Settings` из `ApplicationSettings` + `STMAPISettings` + `GTFSSettings`, singleton `settings`

## Эндпоинты

### `GET /ping`
Healthcheck.

```json
{"status": "ok"}
```

---

### `GET /stm/vehicles`
Позиции всех активных транспортных средств из GTFS-RT.

**Query params:**

| Параметр       | Тип  | Описание                          |
| -------------- | ---- | --------------------------------- |
| `route_id`     | str  | Фильтр по маршруту (напр. `"10"`) |
| `direction_id` | int  | Фильтр по направлению (`0` или `1`) |

**Ответ:** `list[VehiclePosition]`

```json
[
  {
    "id": "...",
    "route_id": "10",
    "direction_id": 0,
    "trip_id": "...",
    "latitude": 45.5017,
    "longitude": -73.5673,
    "bearing": 270.0,
    "speed": 12.5,
    "current_status": 2,
    "stop_id": "52328",
    "occupancy_status": 1,
    "timestamp": 1743700000
  }
]
```

---

### `GET /stm/trips`
Обновления рейсов из GTFS-RT.

**Query params:**

| Параметр            | Тип  | Default | Описание                           |
| ------------------- | ---- | ------- | ---------------------------------- |
| `route_id`          | str  | —       | Фильтр по маршруту                 |
| `direction_id`      | int  | —       | Фильтр по направлению              |
| `include_stop_times` | bool | `false` | Включить `stop_time_updates` в ответ |

**Ответ:** `list[TripUpdate]`

```json
[
  {
    "id": "...",
    "trip_id": "...",
    "route_id": "80",
    "direction_id": 1,
    "start_date": "20260403",
    "stop_time_updates": []
  }
]
```

---

### `GET /stm/stops/{stop_id}/departures`
Ближайшие отправления с остановки из GTFS-RT.

**Path params:**

| Параметр  | Тип | Описание      |
| --------- | --- | ------------- |
| `stop_id` | str | ID остановки  |

**Ответ:** `list[StopDeparture]`

```json
[
  {
    "trip_id": "...",
    "route_id": "10",
    "direction_id": 0,
    "stop_sequence": 14,
    "arrival_time": 1743700120,
    "arrival_delay": 60,
    "departure_time": 1743700140,
    "departure_delay": 60
  }
]
```

---

### `GET /stm/routes/{route_id}`
Агрегированный ответ: позиции транспорта и обновления рейсов по маршруту (параллельный fan-out к `/vehicles` и `/trips`).

**Path params:**

| Параметр   | Тип | Описание      |
| ---------- | --- | ------------- |
| `route_id` | str | ID маршрута   |

**Query params:**

| Параметр             | Тип  | Default | Описание                             |
| -------------------- | ---- | ------- | ------------------------------------ |
| `include_stop_times` | bool | `false` | Включить `stop_time_updates` в рейсы |

**Ответ:** `RouteDetail`

```json
{
  "route_id": "10",
  "vehicles": [...],
  "trips": [...]
}
```

---

### `GET /stm/static/routes/{route_id}`
Статическая информация о маршруте из GTFS.

**Ответ:** `RouteStatic`

```json
{
  "route_id": "747",
  "route_short_name": "747",
  "route_long_name": "Aéroport P.-E.-Trudeau/Montréal",
  "route_type": 3,
  "route_color": "00A6DE"
}
```

---

### `GET /stm/static/routes/{route_id}/trips`
Список рейсов маршрута из GTFS.

**Query params:**

| Параметр       | Тип | Описание                            |
| -------------- | --- | ----------------------------------- |
| `direction_id` | int | Фильтр по направлению (`0` или `1`) |

**Ответ:** `list[TripStatic]`

```json
[
  {
    "trip_id": "...",
    "route_id": "747",
    "direction_id": 0,
    "trip_headsign": "Aéroport",
    "shape_id": "..."
  }
]
```

---

### `GET /stm/static/stops/{stop_id}`
Статическая информация об остановке из GTFS.

**Ответ:** `StopStatic`

```json
{
  "stop_id": "52328",
  "stop_name": "Lionel-Groulx",
  "stop_lat": 45.4732,
  "stop_lon": -73.5700
}
```

## Настройка

Создать `.env` в корне проекта:

```env
TOKEN=your_stm_api_key
```

## Запуск

```bash
# Локально
uv run granian --interface asgi --host 0.0.0.0 --port 8000 core.main:app

# Docker
make run
```

## Команды

```bash
make run       # Собрать и запустить контейнер
make down      # Остановить контейнер
make logs      # Логи контейнера
make rebuild   # Пересобрать с нуля (clear + run)
make check     # ruff lint + format check + ty check
make tests     # Запустить pytest
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

## Roadmap

**Готово**
- [x] Конфигурация через pydantic-settings, Docker / Docker Compose с healthcheck
- [x] HTTP-клиент (`httpx.AsyncClient`) с pre-injected apikey
- [x] Интеграционные тесты (реальный STM API)
- [x] CI/CD: GitHub Actions → GHCR
- [x] `GET /stm/vehicles` — позиции транспорта, фильтрация по `route_id` и `direction_id`
- [x] `GET /stm/trips` — обновления рейсов, фильтрация по маршруту, направлению и флагу `include_stop_times`
- [x] `GET /stm/stops/{stop_id}/departures` — ближайшие отправления с остановки

- [x] `GET /stm/routes/{route_id}` — агрегированный ответ: позиции + рейсы по маршруту

**Следующие шаги**
- [ ] Кэширование GTFS-RT ответов (TTL ~30s) для снижения нагрузки на STM API
- [ ] `GET /stops` — список остановок из GTFS Static

## Референсы

- [nyctrains](https://github.com/arrismo/nyctrains) — аналогичная архитектура для MTA Нью-Йорка
- [gtfs_kit](https://github.com/mrcagney/gtfs_kit) — парсинг GTFS Static
- [morningcashee.com](https://www.morningcashee.com/blog/2024/06/13/getting-realtime-transit-data/) — туториал по STM GTFS-RT на Python
