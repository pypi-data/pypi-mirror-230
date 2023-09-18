from aiohttp import ClientSession
from typing import TypeVar
from .methods.base import Method


T = TypeVar("T")

class WalletPayApi:
    def __init__(
        self,
        api_key: str,
        api_link: str = "https://pay.wallet.tg/wpay/store-api/v1/{}",
        custom_session: ClientSession | None = None,
    ) -> None:
        self._api_key = api_key

        if custom_session is None:
            self.session = ClientSession()
        else:
            self.session = custom_session

        self.base_link = api_link

    def _build_link(self, method: str) -> str:
        return self.base_link.format(method)

    async def __call__(self, method: Method[T]) -> T:
        http_method = method.__http_method__

        url = self._build_link(method.__api_method__)

        headers = {
            "Wpay-Store-Api-Key": self._api_key
        }

        async with self.session.request(
            http_method,
            url,
            headers=headers,
            json=method.to_json(),
            params=method.query_params(),
        ) as r:
            _json = await r.json()

            return method.build_response(_json)

    async def close(self) -> None:
        await self.session.close()
