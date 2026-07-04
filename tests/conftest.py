import os


def pytest_configure():
    os.environ.setdefault("SERPER_API_KEY", "test")
    os.environ.setdefault("GROQ_API_KEY", "test")
    os.environ.setdefault("DATA_ENCRYPTION_KEY", "a" * 44)
    os.environ.setdefault("UNSUBSCRIBE_URL", "https://example.com/unsubscribe")
    os.environ.setdefault("PREFERENCE_CENTER_URL", "https://example.com/preferences")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    os.environ.setdefault("OPT_OUT_LIST", "unsubscribe@example.com")
    os.environ.setdefault("OTLP_ENDPOINT", "http://localhost:4318/v1/traces")
    os.environ.setdefault("OTLP_INSECURE", "True")
