from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "RAG Banking & Health Assistant"
    app_version: str = "0.1.0"
    debug: bool = False

    # Qdrant
    qdrant_url: str
    qdrant_api_key: str

    # Grok
    grok_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
