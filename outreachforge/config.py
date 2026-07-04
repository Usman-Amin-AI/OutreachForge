from pydantic import BaseSettings, Field
from pathlib import Path


class Settings(BaseSettings):
    serper_api_key: str
    groq_api_key: str
    data_encryption_key: str
    unsubscribe_url: str
    preference_center_url: str
    content_directory: str = "./content"
    opt_out_list: str = ""
    audit_log_path: str = "./audit.log"
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    database_url: str = Field("postgresql+psycopg2://user:password@localhost:5432/outreachforge", env="DATABASE_URL")
    otlp_endpoint: str = Field("http://localhost:4318/v1/traces", env="OTLP_ENDPOINT")
    otlp_insecure: bool = Field(True, env="OTLP_INSECURE")

    class Config:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
