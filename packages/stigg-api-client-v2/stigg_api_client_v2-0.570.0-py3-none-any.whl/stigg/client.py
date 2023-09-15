import httpx
from httpx import Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt

from stigg.generated.client import Client
from stigg.generated.async_client import AsyncClient
from stigg.generated import FetchEntitlementsQuery, GetEntitlements, GraphQLClientHttpError, GetPaywallInput, \
    GetPaywall, GraphQlClientInvalidResponseError
from stigg.edge_utils import build_get_entitlements_data, build_get_paywall_data

PRODUCTION_API_URL = "https://api.stigg.io/graphql"
PRODUCTION_EDGE_API_URL = "https://edge.api.stigg.io"

DEFAULT_REQUEST_TIMEOUT = Timeout(timeout=30.0)

STIGG_REQUESTS_RETRY_COUNT = 3
HTTP_TRANSPORT_RETRY_COUNT = 5

RETRY_KWARGS = {
    "retry": (
        retry_if_exception_type(GraphQLClientHttpError) | retry_if_exception_type(GraphQlClientInvalidResponseError)
    ),
    "stop": stop_after_attempt(STIGG_REQUESTS_RETRY_COUNT),
    "reraise": True,
}


class StiggClient(Client):
    def __init__(self, enable_edge: bool, edge_api_url: str, *args, **kwargs):
        self.enable_edge = enable_edge
        self.edge_api_url = edge_api_url

        super().__init__(*args, **kwargs)

    @retry(**RETRY_KWARGS)
    def get_data(self,  *args, **kwargs):
        return super().get_data(*args, **kwargs)

    def get_entitlements(self, query: FetchEntitlementsQuery) -> GetEntitlements:
        if self.enable_edge is False:
            return super().get_entitlements(query)

        url, params = build_get_entitlements_data(self.edge_api_url, query)

        response = self.http_client.get(url=url, params=params)
        data = self.get_data(response)
        return GetEntitlements.parse_obj(data)

    def get_paywall(self, input: GetPaywallInput) -> GetPaywall:
        if self.enable_edge is False:
            return super().get_paywall(input)

        url, params = build_get_paywall_data(self.edge_api_url, input)

        response = self.http_client.get(url=url, params=params)
        data = self.get_data(response)
        return GetPaywall.parse_obj(data)


class AsyncStiggClient(AsyncClient):
    def __init__(self, enable_edge: bool, edge_api_url: str, *args, **kwargs):
        self.enable_edge = enable_edge
        self.edge_api_url = edge_api_url

        super().__init__(*args, **kwargs)

    @retry(**RETRY_KWARGS)
    def get_data(self,  *args, **kwargs):
        return super().get_data(*args, **kwargs)

    async def get_entitlements(self, query: FetchEntitlementsQuery) -> GetEntitlements:
        if self.enable_edge is False:
            return await super().get_entitlements(query)

        url, params = build_get_entitlements_data(self.edge_api_url, query)

        response = await self.http_client.get(url=url, params=params)
        data = self.get_data(response)
        return GetEntitlements.parse_obj(data)

    async def get_paywall(self, input: GetPaywallInput) -> GetPaywall:
        if self.enable_edge is False:
            return await super().get_paywall(input)

        url, params = build_get_paywall_data(self.edge_api_url, input)

        response = await self.http_client.get(url=url, params=params)
        data = self.get_data(response)
        return GetPaywall.parse_obj(data)


def get_headers(api_key: str):
    return {"X-API-KEY": api_key, "Content-Type": "application/json"}


class Stigg:
    @staticmethod
    def create_client(
        api_key: str,
        api_url: str = PRODUCTION_API_URL,
        enable_edge: bool = True,
        edge_api_url: str = PRODUCTION_EDGE_API_URL,
    ) -> StiggClient:
        headers = get_headers(api_key)
        transport = httpx.HTTPTransport(retries=HTTP_TRANSPORT_RETRY_COUNT)
        http_client = httpx.Client(
            headers=headers,
            timeout=DEFAULT_REQUEST_TIMEOUT,
            transport=transport
        )
        return StiggClient(
            enable_edge=enable_edge,
            edge_api_url=edge_api_url,
            url=api_url,
            headers=headers,
            http_client=http_client,
        )

    @staticmethod
    def create_async_client(
        api_key: str,
        api_url: str = PRODUCTION_API_URL,
        enable_edge: bool = True,
        edge_api_url: str = PRODUCTION_EDGE_API_URL,
    ) -> AsyncStiggClient:
        headers = get_headers(api_key)
        transport = httpx.AsyncHTTPTransport(retries=HTTP_TRANSPORT_RETRY_COUNT)
        http_client = httpx.AsyncClient(
            headers=headers,
            timeout=DEFAULT_REQUEST_TIMEOUT,
            transport=transport,
        )
        return AsyncStiggClient(
            enable_edge=enable_edge,
            edge_api_url=edge_api_url,
            url=api_url,
            headers=headers,
            http_client=http_client,
        )
