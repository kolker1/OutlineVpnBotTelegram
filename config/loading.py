from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    BOT_TOKEN: SecretStr
    API_URL_VPN: SecretStr
    CERT_SHA256_VPN: SecretStr
    CARD: SecretStr

    model_config = SettingsConfigDict(
        env_file="config/.env",
        env_file_encoding="utf-8"
    )


config = Config()
