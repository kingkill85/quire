from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "QUIRE_"}

    # Verso connection
    verso_url: str = "http://localhost:3000"

    # Server
    host: str = "0.0.0.0"
    port: int = 8085

    # Cloudflare bypass
    cf_bypass: str = "none"  # "none", "internal", "external"
    flaresolverr_url: str = "http://flaresolverr:8191/v1"

    # Downloads
    temp_dir: str = "/tmp/quire"
    max_concurrent_downloads: int = 3

    # Sources
    annas_archive_api_key: str = ""
    zlibrary_email: str = ""
    zlibrary_password: str = ""


settings = Settings()
