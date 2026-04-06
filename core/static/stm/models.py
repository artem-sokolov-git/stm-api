from sqlalchemy import Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Route(Base):
    __tablename__ = "routes"

    route_id: Mapped[str] = mapped_column(Text, primary_key=True)
    route_short_name: Mapped[str] = mapped_column(Text, nullable=False)
    route_long_name: Mapped[str] = mapped_column(Text, nullable=False)
    route_type: Mapped[int] = mapped_column(Integer, nullable=False)
    route_color: Mapped[str | None] = mapped_column(Text)


class Stop(Base):
    __tablename__ = "stops"

    stop_id: Mapped[str] = mapped_column(Text, primary_key=True)
    stop_name: Mapped[str] = mapped_column(Text, nullable=False)
    stop_lat: Mapped[float] = mapped_column(nullable=False)
    stop_lon: Mapped[float] = mapped_column(nullable=False)


class Trip(Base):
    __tablename__ = "trips"

    trip_id: Mapped[str] = mapped_column(Text, primary_key=True)
    route_id: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    direction_id: Mapped[int] = mapped_column(Integer, nullable=False)
    trip_headsign: Mapped[str | None] = mapped_column(Text)
    shape_id: Mapped[str | None] = mapped_column(Text)
