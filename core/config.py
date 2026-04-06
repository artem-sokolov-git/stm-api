from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


class ApplicationSettings(EnvBaseSettings):
    token: SecretStr


class STMAPISettings(EnvBaseSettings):
    gtfs_url: str = "https://api.stm.info/pub/od/gtfs-rt/ic/v2"
    status_url: str = "https://api.stm.info/pub/od/i3/v2/messages"

    @property
    def position_endpoint(self) -> str:
        return f"{self.gtfs_url}/vehiclePositions"

    @property
    def trip_updates_endpoint(self) -> str:
        return f"{self.gtfs_url}/tripUpdates"

    @property
    def service_status_endpoint(self) -> str:
        return f"{self.status_url}/etatservice"


class GTFSSettings(EnvBaseSettings):
    gtfs_static_url: str = "https://www.stm.info/sites/default/files/gtfs/gtfs_stm.zip"
    gtfs_db_path: str = "gtfs.db"
    gtfs_max_age_days: int = 7


class Settings(ApplicationSettings, STMAPISettings, GTFSSettings):
    pass


settings = Settings()  # ty:ignore[missing-argument]
