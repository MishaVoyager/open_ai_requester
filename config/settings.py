from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    """Общие настройки"""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra="allow"
    )

    OPENAI_API_KEY: str
    DRY_MODE: bool
