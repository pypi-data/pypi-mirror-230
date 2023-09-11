from .brokerage import iex, rest
from .brokerage.ibkr import DAMECAClient, DAMFBClient
from .brokerage.vars import BrokerSettings, IEXSettings


class Portal:
    broker_settings = BrokerSettings()
    iex_settings = IEXSettings()

    def __apca_config_exist(self):
        config = all(
            [
                self.broker_settings.BROKER_KEY,
                self.broker_settings.BROKER_SECRET,
                self.broker_settings.BROKER_API_URL,
                self.broker_settings.MARKET_API_URL,
                self.iex_settings.IEX_API_URL,
                self.iex_settings.IEX_TOKEN,
            ]
        )
        if not config:
            raise NotImplementedError("ALPACA env Config not set")

    def __iex_config_exist(self):
        config = all(
            [
                self.iex_settings.IEX_API_URL,
                self.iex_settings.IEX_TOKEN,
            ]
        )
        if not config:
            raise NotImplementedError("IEX env Config not set")

    def get_broker_client(self) -> rest.Broker:
        self.__apca_config_exist()
        return rest.Broker()

    def get_market_client(self) -> rest.MarketData:
        self.__apca_config_exist()

        return rest.MarketData()

    def get_event_client(self) -> rest.BrokerEvents:
        self.__apca_config_exist()
        return rest.BrokerEvents()

    def get_iex_client(self) -> iex.PriceData:
        self.__iex_config_exist()
        return iex.PriceData()


class IBClient:
    @classmethod
    def get_ECA_client(cls) -> DAMECAClient:
        return DAMECAClient()

    @classmethod
    def get_FB_client(cls) -> DAMFBClient:
        return DAMFBClient()
