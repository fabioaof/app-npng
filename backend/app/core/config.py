from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_CORS = (
    "http://localhost:9000,http://127.0.0.1:9000,"
    "http://localhost:8090,http://127.0.0.1:8090,"
    "http://localhost:8080,http://127.0.0.1:8080,"
    "http://localhost:5173,http://127.0.0.1:5173"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "NP-NG API"
    api_prefix: str = "/api"

    database_url: str = "postgresql+psycopg://npng:npng@localhost:5432/npng"
    jwt_secret: str = "change-me-in-production-use-long-random-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7

    # Lista separada por vírgulas. Se CORS_ORIGINS estiver vazio no .env, usa o default.
    cors_origins: str = _DEFAULT_CORS

    @field_validator("cors_origins", mode="before")
    @classmethod
    def cors_origins_non_empty(cls, v: object) -> str:
        if v is None or (isinstance(v, str) and not v.strip()):
            return _DEFAULT_CORS
        return str(v).strip()
    upload_dir: str = "./uploads"
    public_base_url: str = "http://localhost:8000"


settings = Settings()
