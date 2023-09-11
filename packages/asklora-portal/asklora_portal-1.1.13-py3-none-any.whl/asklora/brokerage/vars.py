from pydantic import BaseSettings, Field


class BrokerLoggerSettings(BaseSettings):
    LOGGER_LEVEL: str = Field("INFO", env="BROKER_LOGGER_LEVEL")

    class Config:
        env_file = ".env"


class PortalLoggerSettings(BaseSettings):
    LOGGER_LEVEL: str = Field("INFO", env="PORTAL_LOGGER_LEVEL")
    LOG_FILE: str = Field("portal.log", env="PORTAL_LOG_FILE")

    class Config:
        env_file = ".env"


class BrokerSettings(BaseSettings):
    BROKER_KEY: str | None = Field(None, env="BROKER_KEY")
    BROKER_SECRET: str | None = Field(None, env="BROKER_SECRET")
    BROKER_API_URL: str | None = Field(None, env="BROKER_API_URL")

    MARKET_API_URL: str | None = Field(None, env="MARKET_API_URL")

    @property
    def not_set(self):
        return not all(
            [
                self.BROKER_KEY,
                self.BROKER_SECRET,
                self.BROKER_API_URL,
                self.MARKET_API_URL,
            ]
        )

    class Config:
        env_file = ".env"


class IEXSettings(BaseSettings):
    IEX_API_URL: str | None = Field(None, env="IEX_API_URL")
    IEX_TOKEN: str | None = Field(None, env="IEX_TOKEN")
    IEX_RETRY_MAX: int = Field(3, env="IEX_RETRY_MAX")
    IEX_RETRY_WAIT: int = Field(3, env="IEX_RETRY_WAIT")
    IEX_RETRY_CODES: str = Field("429,504", env="IEX_RETRY_CODES")

    @property
    def not_set(self):
        return not all([self.IEX_TOKEN, self.IEX_API_URL])

    class Config:
        env_file = ".env"


class DAMSettings(BaseSettings):
    DAM_URL: str = Field(..., env="DAM_URL")
    DAM_CSID: str = Field(..., env="DAM_CSID")

    @property
    def DAM_CA_URL(self):
        return self.DAM_URL.rstrip("/") + "/ws/cacapi.ext/submit"

    @property
    def DAM_ECA_URL(self):
        return self.DAM_URL.rstrip("/") + "/ws/eca/"

    @property
    def DAM_FB_URL(self):
        return self.DAM_URL.rstrip("/") + "/ws/fb/"

    class Config:
        env_file = ".env"
