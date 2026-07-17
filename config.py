import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    gemini_api_key: str
    ship_admin_token: str
    safe_sandbox_dir: Path

    @field_validator("safe_sandbox_dir")
    def validate_and_create_sandbox(cls, v: Path) -> Path:
        abs_path = v.resolve()
        os.makedirs(abs_path, exist_ok=True)
        return abs_path

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()