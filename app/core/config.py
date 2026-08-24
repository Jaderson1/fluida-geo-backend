from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/fluida_geo"

    # Comma-separated, not JSON — simpler to set by hand via `fly secrets`
    # or a platform's env var UI than quoting a list.
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    allowed_hosts: str = "*"

    enable_api_docs: bool = True
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_prefix="")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]


settings = Settings()