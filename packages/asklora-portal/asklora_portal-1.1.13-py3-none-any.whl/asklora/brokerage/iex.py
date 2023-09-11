from asklora.brokerage.client import BaseRestClient
from asklora.brokerage.vars import IEXSettings


class PriceData(BaseRestClient):
    def __init__(self):
        iex_settings = IEXSettings()
        self._token = iex_settings.IEX_TOKEN

        super().__init__(
            base_url=iex_settings.IEX_API_URL,
            retry_max_count=iex_settings.IEX_RETRY_MAX,
            retry_wait_time=iex_settings.IEX_RETRY_WAIT,
            retry_status_codes=iex_settings.IEX_RETRY_CODES,
        )

    def get_quote(self, symbol: str):
        data = self.get(f"/v1/data/CORE/QUOTE/{symbol.upper()}?token={self._token}")[0]
        return data or None

    def get_company(self, symbol: str):
        data = self.get(f"/v1/data/CORE/COMPANY/{symbol.upper()}?token={self._token}")[0]  # type: ignore
        return data or None

    def get_lastestPrice(self, symbol: str):
        result: dict | None = self.get_quote(symbol)
        return result.get("latestPrice", None) if result else None

    def get_marketOpen(self, symbol: str = "MSFT"):
        result: dict | None = self.get_quote(symbol)
        return result.get("isUSMarketOpen", False) if result else None
