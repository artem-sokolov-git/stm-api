from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from core.static.stm.loader import download_zip, parse_zip
from core.static.stm.models import Base, Route, Stop, Trip


def is_fresh(db_path: str, max_age_days: int) -> bool:
    path = Path(db_path)
    if not path.exists():
        return False
    age = datetime.now() - datetime.fromtimestamp(path.stat().st_mtime)
    return age.days < max_age_days


class StaticDB:
    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    async def open(self, db_path: str) -> None:
        self._engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    async def load(self, zip_url: str) -> None:
        assert self._engine is not None

        zip_bytes = await download_zip(zip_url)
        data = parse_zip(zip_bytes)

        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with self._session_factory() as session:  # type: ignore[misc]
            session.add_all([Route(**row) for row in data["routes"]])
            session.add_all([Stop(**row) for row in data["stops"]])
            session.add_all([Trip(**row) for row in data["trips"]])
            await session.commit()

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    def session(self) -> AsyncSession:
        if self._session_factory is None:
            raise RuntimeError("StaticDB is not open")
        return self._session_factory()


db = StaticDB()
