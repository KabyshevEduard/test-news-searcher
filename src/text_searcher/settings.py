from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import logging

class Settings(BaseSettings):
    DB_FILE: str
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

    model_config = SettingsConfigDict(env_file=f"{BASE_DIR}/.env")


settings = Settings()