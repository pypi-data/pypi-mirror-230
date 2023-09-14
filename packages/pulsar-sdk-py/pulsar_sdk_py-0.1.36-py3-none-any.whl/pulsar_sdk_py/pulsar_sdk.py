import re
import json
import uuid
import logging
from dataclasses import asdict

import requests
import websockets
from typing import AsyncGenerator

from pulsar_sdk_py.helpers import filter_non_empty_params
from pulsar_sdk_py.dataclasses.serializer import serialize_to_dataclass
from pulsar_sdk_py.enums import (
    TierKeys,
    ChainKeys,
    TokenSort,
    TokenType,
    NFTItemSort,
    ProtocolSort,
    NFTCollectionSort,
    replace_enums_with_values,
)
from pulsar_sdk_py.exceptions import (
    WebSocketClosed,
    SerializationError,
    WrongResponseFormat,
)
from pulsar_sdk_py.dataclasses.schemas import (
    NFTItem,
    Timeseries,
    ResolvedName,
    ProtocolData,
    NFTCollection,
    ExtendedToken,
    ResolvedAddress,
    NFTTraitsFilter,
    PaginatedNFTItem,
    ProtocolTimeseries,
    TimeseriesWithStats,
    TokenPriceTimeseries,
    AggregateWalletTokens,
    WalletRequestSettings,
    PaginatedNFTCollection,
    PaginatedTokenWithStats,
    PaginatedProtocolWithStats,
    AggregateWalletIntegrations,
    WalletNFTsErrors,
)


class PulsarSDK:
    """
    A client for interacting with the Pulsar Third Party API.

    This class provides a high-level interface for interacting with the API, including the ability to
    retrieve data about tokens, domain names, NFTs, protocols, and wallet balances. The class serves typified ways to
    interact with the endpoints, through websockets or REST.

    Args:
        api_key (str): The API key to use for making requests to the Pulsar Third Party API.

    """

    _BASE_URL = "qa-api.pulsar.finance"

    @property
    def REST_API_URL(self):
        return f"{self._PROTOCOL}://{self._BASE_URL}/v1/thirdparty"

    @property
    def WS_API_URL(self):
        return f"{self._WS_PROTOCOL}://{self._BASE_URL}/v1/thirdparty/ws"

    def __init__(self, api_key, base_url: str | None = None, use_ssl: bool = True):
        if base_url:
            self._BASE_URL = base_url

        self._PROTOCOL = "https" if use_ssl else "http"
        self._WS_PROTOCOL = "wss" if use_ssl else "ws"
        headers = {"Authorization": f"Bearer {api_key}"}

        # Rest clients
        self.tokens = self._TokenRestClient(rest_api_url=self.REST_API_URL, headers=headers)
        self.name_service = self._NameServiceRestClient(rest_api_url=self.REST_API_URL, headers=headers)
        self.nfts = self._NFTRestClient(rest_api_url=self.REST_API_URL, headers=headers)
        self.protocols = self._ProtocolRestClient(rest_api_url=self.REST_API_URL, headers=headers)
        self.wallets = self._WalletRestClient(rest_api_url=self.REST_API_URL, headers=headers)

        # Websocket clients
        ws_client = PulsarSDK._WebsocketClient(ws_url=self.WS_API_URL, api_key=api_key)
        self.balances = self._WalletBalancesClient(ws_client=ws_client)

    class _WebsocketClient:
        # noinspection PyUnresolvedReferences
        """
        A helper class for making WebSocket connections to a third-party service.

        This class provides methods for establishing and managing WebSocket connections to a third-party service. It
        includes a method for generating responses from a WebSocket connection, as well as methods for handling
        responses and processing payload data.

        Attributes: headers (dict): A dictionary of headers to include in WebSocket connection requests sent by
        instances of this class. uri (str): The URI for the WebSocket connection. websocket_conn: The WebSocket
        connection object.

        """

        headers = {}
        websocket_conn = None

        def __init__(self, ws_url, api_key):
            self.WS_URL = ws_url
            self.headers = {"Authorization": api_key}

        async def __connect_websocket(self):
            """
            Establish a WebSocket connection.

            This method establishes a WebSocket connection to the specified URI, using the headers provided to the
            instance.

            Returns:
                The WebSocket connection object.

            """
            if self.websocket_conn is not None and self.websocket_conn.open:
                # WebSocket connection is already open, return the existing connection
                return self.websocket_conn

            # Create a new WebSocket connection
            self.websocket_conn = await websockets.connect(self.WS_URL, extra_headers=self.headers)
            return self.websocket_conn

        async def response_generator(self, msg):
            """
            Generate responses from a WebSocket connection.

            This method sends a message to the WebSocket connection, and then waits for responses to be received from
            the connection. It generates each response as it is received.

            Args:
                msg (dict): A dictionary representing the message to send over the WebSocket connection.

            Yields:
                str: The response received from the WebSocket connection.

            Raises:
                WebSocketClosed: If the WebSocket connection is unexpectedly closed while waiting for responses.

            """
            try:
                websocket_conn = await self.__connect_websocket()
                serialized_data = json.dumps(msg)
                await websocket_conn.send(serialized_data)
                while True:
                    yield await websocket_conn.recv()
            except websockets.ConnectionClosed as e:
                # Handle connection closed error
                raise WebSocketClosed(
                    f"Connection unexpectedly closed while waiting for responses from request ID: {msg['request_id']}"
                ) from e
            except Exception as e:
                # Handle other exceptions that may occur
                logging.error(f"Exception occurred while waiting for responses from request ID: {msg['request_id']}")
                raise e

        async def handle_response(self, request_id, msg, finished_event_type):
            """
            Handle responses received from a WebSocket connection.

            This method generates responses from a WebSocket connection, and then processes the payload data in each
            response. If the response contains a "finished" event of the specified type, the method returns.

            Args:
                request_id (str): The ID of the request associated with the WebSocket connection.
                msg (dict): A dictionary representing the message to send over the WebSocket connection.
                finished_event_type (str): The event type indicating that the request has finished.

            Yields:
                Any: The processed payload data from the response.

            Raises:
                WebSocketClosed: If the WebSocket connection is unexpectedly closed while waiting for responses.
                WrongResponseFormat: If a response does not contain the expected data format.

            """
            async for response in self.response_generator(msg):
                try:
                    event_dict = await self.__get_event_dict(request_id=request_id, response=response)
                    if event_dict:
                        event_type = event_dict["key"]
                        if "PREFETCH" not in event_type:
                            if event_payload := event_dict["payload"]:
                                payload_type = event_payload["type"]
                                payload_data = event_payload["data"]
                                async for item in self.__process_payload(payload_type, payload_data):
                                    yield item
                        if event_type == finished_event_type:
                            return
                    # TODO this is missing error handling if the response field is_error is True
                except WrongResponseFormat as e:
                    logging.error(f"Response from API is not valid. Request ID: {request_id}")
                    raise e

        @staticmethod
        async def __process_payload(payload_type, payload_data):
            """
            Process the payload data in a WebSocket response.

            This method processes the payload data in a WebSocket response, converting it to a more easily usable
            format.

            Args:
                payload_type (str): The type of the payload data in the response.
                payload_data (dict): The payload data to process.

            Yields:
                Any: The processed payload data from the response.

            Raises:
                SerializationError: If an error occurs during serialization of the payload data.

            """
            try:
                if payload_type.startswith("Timeseries"):
                    yield serialize_to_dataclass(payload_data[0], Timeseries)
                elif payload_type.startswith("AggregateWalletIntegrations"):
                    yield serialize_to_dataclass(payload_data, AggregateWalletIntegrations)
                elif payload_type.startswith("NFTItem"):
                    yield serialize_to_dataclass(payload_data, WalletNFTsErrors)
                elif payload_type.startswith("AggregateWalletTokens"):
                    yield serialize_to_dataclass(payload_data, AggregateWalletTokens)
            except Exception as e:
                # Handle serialization error
                raise SerializationError(
                    f"An error occurred during serialization: {str(e)}\nSerializing {payload_type}."
                ) from e

        @staticmethod
        async def __get_event_dict(request_id, response):
            """
            A coroutine that returns the event dictionary from the WebSocket server response.

            This method is responsible for parsing the response from the WebSocket server and returning the event
            dictionary contained within.

            Args:
                request_id (str): The ID of the request being made.
                response (str): The response received from the WebSocket server.

            Returns:
                The event dictionary contained within the WebSocket server response.

            Raises:
                WrongResponseFormat: If the response from the WebSocket server is not in the expected format.

            """
            json_response = json.loads(response)
            event_dict = json_response.get("event")
            if not event_dict:
                raise WrongResponseFormat("Response does not contain 'event' dictionary.")
            if "request_id" not in event_dict:
                raise WrongResponseFormat("Response 'event' dictionary does not contain 'request_id' key.")
            if event_dict["request_id"] == request_id:
                return event_dict

    class _WalletBalancesClient:
        __KEYS = {
            "WALLET_BALANCES": {
                "COMMAND": "WALLET_BALANCES",
                "FINISHED": "WALLET_BALANCES_FINISHED",
            },
            "GET_WALLET_TIMESERIES": {
                "COMMAND": "GET_WALLET_TIMESERIES",
                "FINISHED": "GET_WALLET_TIMESERIES_FINISHED",
            },
        }

        def __init__(self, ws_client):
            self.__ws_client = ws_client

        @replace_enums_with_values
        async def get_wallet_balances(
            self, wallet_addr: str, chain: ChainKeys, wallet_request_settings: WalletRequestSettings | None = None
        ) -> AsyncGenerator[AggregateWalletIntegrations | list[NFTItem] | AggregateWalletTokens | None, None]:
            request_id = str(uuid.uuid4())

            data_dict = {"address": wallet_addr, "chain": chain}
            if wallet_request_settings:
                self.__convert_sets_to_lists(wallet_request_settings)
                data_dict |= asdict(wallet_request_settings)

            msg = {
                "method": "COMMAND",
                "command": {
                    "key": f"{self.__KEYS['WALLET_BALANCES']['COMMAND']}",
                    "data": data_dict,
                },
                "request_id": request_id,
            }
            finished_event_type = self.__KEYS["WALLET_BALANCES"]["FINISHED"]
            async for response in self.__ws_client.handle_response(
                request_id=request_id,
                msg=msg,
                finished_event_type=finished_event_type,
            ):
                yield response

        @replace_enums_with_values
        async def get_wallet_timeseries(
            self, wallet_addr: str, chain: ChainKeys, tier: TierKeys
        ) -> AsyncGenerator[Timeseries, None]:
            request_id = str(uuid.uuid4())
            msg = {
                "method": "COMMAND",
                "command": {
                    "key": f"{self.__KEYS['GET_WALLET_TIMESERIES']['COMMAND']}",
                    "data": {
                        "address": f"{wallet_addr}",
                        "chain": f"{chain}",
                        "tier": f"{tier}",
                    },
                },
                "request_id": request_id,
            }
            finished_event_type = self.__KEYS["GET_WALLET_TIMESERIES"]["FINISHED"]
            async for response in self.__ws_client.handle_response(
                request_id=request_id,
                msg=msg,
                finished_event_type=finished_event_type,
            ):
                yield response

        def __convert_sets_to_lists(self, wallet_request_settings: WalletRequestSettings):
            wallet_request_settings.hide_nfts = list(wallet_request_settings.hide_nfts)
            wallet_request_settings.hide_tokens = list(wallet_request_settings.hide_tokens)
            wallet_request_settings.hide_integrations = list(wallet_request_settings.hide_integrations)

    class _RestClient:
        # noinspection PyUnresolvedReferences
        """
        A helper class for making HTTP requests to a REST API.

        This class provides several methods for sending HTTP requests to Pulsar REST API endpoints.
        It includes a static method for filtering out any key-value pairs from a dictionary where the value is None,
        as well as a method for sending an HTTP request to a Pulsar REST API endpoint and returning the JSON
        response body.

        Attributes:
            headers (dict): A dictionary of headers to include in HTTP requests sent by instances of this class.

        """

        headers = {}

        def __init__(self, rest_api_url, headers):
            self.REST_API_URL = rest_api_url
            self.headers = headers

        @replace_enums_with_values
        def __get_request_on_endpoint(self, func_name, request_type, request_body=None, **kwargs):
            """
            Send an HTTP request to a specific REST API endpoint and return the JSON response body.

            Args:
                func_name (str): The name of a function that corresponds to a specific REST API endpoint.
                request_type (str): The HTTP method to use for the request (e.g. "GET", "POST", "PUT").
                request_body (dict, optional): The JSON payload to include in the request body (default: {}).
                **kwargs: Key-value pairs to include as path or query parameters in the request URL.

            Returns:
                dict: The JSON response body as a dictionary.

            Raises:
                HTTPError: If the response from the API endpoint indicates an error status code (e.g. 4xx or 5xx).

            """
            if request_body is None:
                request_body = {}
            endpoint_url = self.endpoints[func_name]

            # This code extracts named parameters from a string (endpoint_url) using regular expressions,
            # and populates them with corresponding values from a dictionary (kwargs).The resulting string is formed
            # by substituting the named parameters with their corresponding values, and concatenating the result with
            # another string (BASE_URL).
            param_names = re.findall(r"\{([^{}]*)\}", endpoint_url)
            params = {}
            for param_name in param_names:
                if param_name in kwargs:
                    param_value = kwargs.pop(param_name)
                    params[param_name] = param_value
            formatted_url = endpoint_url.format(**params)
            endpoint_url = self.REST_API_URL + formatted_url

            if kwargs:
                # If there are any remaining kwargs, construct them as query parameters for the endpoint URL
                query_params = []
                for key, value in kwargs.items():
                    if isinstance(value, list):
                        query_params.extend(f"{key}={item}" for item in value)
                    else:
                        query_params.append(f"{key}={value}")
                query_params_string = "&".join(query_params)
                endpoint_url += f"?{query_params_string}"  # Add the query parameters to the endpoint URL

            response = requests.request(
                method=request_type,
                url=endpoint_url,
                json=request_body,
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()

    class _NameServiceRestClient(_RestClient):
        endpoints = {
            "resolve_name": "/name-service/resolve-name",
            "resolve_address": "/name-service/resolve-address",
        }

        # NAME SERVICE
        def resolve_name(self, name: str) -> ResolvedName:
            response = self._RestClient__get_request_on_endpoint(
                func_name="resolve_name", request_type="GET", name=name
            )
            return serialize_to_dataclass(response, ResolvedName)

        def resolve_address(self, address: str) -> ResolvedAddress:
            response = self._RestClient__get_request_on_endpoint(
                func_name="resolve_address", request_type="GET", address=address
            )
            return serialize_to_dataclass(response, ResolvedAddress)

    class _ProtocolRestClient(_RestClient):
        endpoints = {
            "get_protocol": "/protocols/protocols/{protocol_key}",
            "list_protocols": "/protocols/all-protocols",
            "get_number_protocols": "/protocols/total-protocols",
            "get_filtered_protocols": "/protocols",
            "get_protocol_timeseries": "/protocols/{protocol_key}/timeseries",
        }

        def get_protocol(self, protocol_key: str) -> ProtocolData:
            response = self._RestClient__get_request_on_endpoint(
                func_name="get_protocol", request_type="GET", protocol_key=protocol_key
            )
            return serialize_to_dataclass(response, ProtocolData)

        def list_protocols(self, chain: ChainKeys | None = None) -> list[ProtocolData]:
            params_filtered = filter_non_empty_params(chain=chain)
            response = self._RestClient__get_request_on_endpoint(
                func_name="list_protocols", request_type="GET", **params_filtered
            )
            return [serialize_to_dataclass(protocol, ProtocolData) for protocol in response]

        def get_number_protocols(self) -> int:
            return self._RestClient__get_request_on_endpoint("get_number_protocols", request_type="GET")

        def get_filtered_protocols(
            self,
            name: str | None = None,
            chains: list[ChainKeys] | None = None,
            tvl: str | None = None,
            sort_by: ProtocolSort | None = None,
            offset: int = 0,
            limit: int = 10,
        ) -> PaginatedProtocolWithStats:
            params_filtered = filter_non_empty_params(
                name=name,
                chains=chains,
                tvl=tvl,
                sort_by=sort_by,
                offset=offset,
                limit=limit,
            )
            response = self._RestClient__get_request_on_endpoint(
                func_name="get_filtered_protocols",
                request_type="GET",
                **params_filtered,
            )
            return serialize_to_dataclass(response, PaginatedProtocolWithStats)

        def get_protocol_timeseries(self, protocol_key: str, tier_name: TierKeys) -> ProtocolTimeseries:
            response = self._RestClient__get_request_on_endpoint(
                func_name="get_protocol_timeseries",
                request_type="GET",
                protocol_key=protocol_key,
                tier_name=tier_name,
            )
            return serialize_to_dataclass(response, ProtocolTimeseries)

    class _NFTRestClient(_RestClient):
        endpoints = {
            "fetch_collection_by_address": "/nfts/collections/{chain}/{collection_address}",
            "fetch_nft_by_address": "/nfts/collections/{chain}/{collection_address}/nfts",
            "list_collection_nfts": "/nfts/collections/{collection_id}/nfts",
            "fetch_nft": "/nfts/collections/{collection_id}/nfts/{token_id}",
            "fetch_collection": "/nfts/collections/{collection_id}",
            "list_nfts": "/nfts",
        }

        def list_collection_nfts(
            self,
            collection_id: str,
            search_string: str | None = None,
            rarity_score: str | None = None,
            rank_minimum: int | None = None,
            rank_maximum: int | None = None,
            traits: NFTTraitsFilter | None = None,
            sort_by: NFTItemSort | None = None,
            offset: int = 0,
            limit: int = 10,
        ) -> PaginatedNFTItem:
            params_filtered = filter_non_empty_params(
                collection_id=collection_id,
                search_string=search_string,
                rarity_score=rarity_score,
                rank_minimum=rank_minimum,
                rank_maximum=rank_maximum,
                sort_by=sort_by,
                offset=offset,
                limit=limit,
            )

            traits_dict = {"traits": [] if traits is None else traits.traits}

            response = self._RestClient__get_request_on_endpoint(
                func_name="list_collection_nfts",
                request_type="POST",
                request_body=traits_dict,
                **params_filtered,
            )
            return serialize_to_dataclass(response, PaginatedNFTItem)

        def fetch_collection(self, collection_id: str) -> NFTCollection:
            response = self._RestClient__get_request_on_endpoint(
                func_name="fetch_collection",
                request_type="GET",
                collection_id=collection_id,
            )
            return serialize_to_dataclass(response, NFTCollection)

        def fetch_collection_by_address(self, collection_address: str, chain: ChainKeys) -> NFTCollection:
            response = self._RestClient__get_request_on_endpoint(
                func_name="fetch_collection_by_address",
                request_type="GET",
                collection_address=collection_address,
                chain=chain,
            )
            return serialize_to_dataclass(response, NFTCollection)

        def fetch_nft(self, collection_id: str, token_id: str) -> NFTItem:
            response = self._RestClient__get_request_on_endpoint(
                func_name="fetch_nft",
                request_type="GET",
                collection_id=collection_id,
                token_id=token_id,
            )
            return serialize_to_dataclass(response, NFTItem)

        def fetch_nft_by_address(self, collection_address: str, chain: ChainKeys, token_id: str) -> NFTItem:
            response = self._RestClient__get_request_on_endpoint(
                func_name="fetch_nft_by_address",
                request_type="GET",
                collection_address=collection_address,
                chain=chain,
                token_id=token_id,
            )
            return serialize_to_dataclass(response, NFTItem)

        def list_nfts(
            self,
            name: str | None = None,
            chains: list[ChainKeys] | None = None,
            sort_by: NFTCollectionSort | None = None,
            offset: int = 0,
            limit: int = 10,
            is_fully_index: bool = True,
        ) -> PaginatedNFTCollection:
            params_filtered = filter_non_empty_params(
                name=name,
                chains=chains,
                sort_by=sort_by,
                offset=offset,
                limit=limit,
                is_fully_index=is_fully_index,
            )
            response = self._RestClient__get_request_on_endpoint(
                func_name="list_nfts", request_type="GET", **params_filtered
            )
            return serialize_to_dataclass(response, PaginatedNFTCollection)

    class _TokenRestClient(_RestClient):
        endpoints = {
            "get_token_info_by_id": "/token/{token_id}",
            "get_token_info_by_address_and_chain": "/token/{token_type}/{address}",
            "list_tokens": "/tokens",
            "get_token_timeseries": "/tokens/{token_id}/timeseries",
        }

        # TOKENS
        def get_token_info_by_id(self, token_id: str) -> ExtendedToken:
            response = self._RestClient__get_request_on_endpoint(
                func_name="get_token_info_by_id", request_type="GET", token_id=token_id
            )
            return serialize_to_dataclass(response, ExtendedToken)

        def get_token_info_by_address_and_chain(
            self, token_type: TokenType, address: str, chain: ChainKeys
        ) -> ExtendedToken:
            response = self._RestClient__get_request_on_endpoint(
                func_name="get_token_info_by_address_and_chain",
                request_type="GET",
                token_type=token_type,
                address=address,
                chain=chain,
            )
            return serialize_to_dataclass(response, ExtendedToken)

        def list_tokens(
            self,
            text: str | None = None,
            chains: list[ChainKeys] | None = None,
            minimum_liquidity: int = 0,
            sort_by: TokenSort | None = None,
            whitelisted_only: bool = False,
            remove_blacklisted: bool = False,
            offset: int = 0,
            limit: int = 10,
        ) -> PaginatedTokenWithStats:
            params_filtered = filter_non_empty_params(
                text=text,
                chains=chains,
                sort_by=sort_by,
                offset=offset,
                limit=limit,
                minimum_liquidity=minimum_liquidity,
                whitelisted_only=whitelisted_only,
                remove_blacklisted=remove_blacklisted,
            )
            response = self._RestClient__get_request_on_endpoint(
                func_name="list_tokens", request_type="GET", **params_filtered
            )
            return serialize_to_dataclass(response, PaginatedTokenWithStats)

        def get_token_timeseries(self, token_id: str, tier_name: TierKeys) -> TokenPriceTimeseries:
            response = self._RestClient__get_request_on_endpoint(
                func_name="get_token_timeseries",
                request_type="GET",
                token_id=token_id,
                tier_name=tier_name,
            )
            return serialize_to_dataclass(response, TokenPriceTimeseries)

    class _WalletRestClient(_RestClient):
        endpoints = {
            "get_wallet_timeseries": "/wallet/{address}/timeseries",
        }

        def get_wallet_timeseries(
            self, address: str, chain: ChainKeys, tier: TierKeys = TierKeys.ONE_DAY
        ) -> TimeseriesWithStats:
            response = self._RestClient__get_request_on_endpoint(
                func_name="get_wallet_timeseries",
                request_type="GET",
                address=address,
                chain=chain,
                tier=tier,
            )
            return serialize_to_dataclass(response, TimeseriesWithStats)
