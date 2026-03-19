from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    enable_insider_trading_xbrl: bool = False

    model_config = SettingsConfigDict(
        env_prefix="NSE_CORPORATE_DATA_",
        extra="ignore",
    )


def get_settings() -> Settings:
    return Settings()
