# STB API client

import os
from typing import Any, Dict, Optional, Type, Unpack
from json import JSONDecodeError

from pandas import DataFrame, json_normalize, concat

from urllib.parse import urlparse
from urllib.parse import parse_qs

from apiclient import (
    endpoint,
    paginated,
    retry_request,
    HeaderAuthentication,
    JsonRequestFormatter,
)

from apiclient.response import Response
from apiclient.exceptions import APIClientError, ResponseParseError
from apiclient.authentication_methods import BaseAuthenticationMethod
from apiclient.response_handlers import BaseResponseHandler
from apiclient.request_formatters import BaseRequestFormatter
from apiclient.request_strategies import (
    BaseRequestStrategy,
    # QueryParamPaginatedRequestStrategy,
)
from apiclient.utils.typing import OptionalJsonType
from apiclient.error_handlers import BaseErrorHandler, ErrorHandler

API_KEY: str | None = os.environ.get("STB_API_KEY")
assert API_KEY is not None, "Please set the STB_API_KEY environment variable"

from tihclient.base import BaseClient

authentication_method = HeaderAuthentication(
    token=API_KEY,
    parameter="x-api-key",
    scheme=None,
)


def get_next_page(response: Response, *_) -> Response:
    """Get the next page of results from a paginated response."""
    # Check if the next page is the last page
    if "next" not in response["paginationLinks"]:
        return None
    # Get the next page URL
    parse_url = urlparse(response["paginationLinks"]["next"])
    # Get the query parameters
    query_params = parse_qs(parse_url.query)
    # Get the offset
    offset = query_params["offset"][0]
    # Get the limit
    limit = query_params["limit"][0]

    # Return the next page
    return {
        "limit": limit,
        "offset": offset,
    }


# Define endpoints, using the provided decorator.
@endpoint(base_url="https://api.stb.gov.sg/content")
class Endpoint:
    """STB API endpoints"""

    accommodation: str = "accommodation/v2/search"
    attractions: str = "attractions/v2/search"
    attraction: str = "attractions/v2/search/{uuid}"
    bars_clubs: str = "bars-clubs/v2/search"
    cruises: str = "cruises/v2/search"
    events: str = "events/v2/search"
    event: str = "events/v2/search/{uuid}"
    food_beverages: str = "food-beverages/v2/search"
    precincts: str = "precincts/v2/search"
    precinct: str = "precincts/v2/search/{uuid}"
    shops: str = "shops/v2/search"
    tours: str = "tours/v2/search"
    tour: str = "tours/v2/search/{uuid}"
    venues: str = "venues/v2/search"
    walking_trails: str = "walking-trails/v2/search"
    walking_trail: str = "walking-trails/v2/details/{uuid}"


# Define endpoints, using the provided decorator.
@endpoint(base_url="https://api.stb.gov.sg/services/navigation/v2")
class MapEndpoint:
    """STB API endpoints"""

    autocomplete: str = "autocomplete"
    place_details: str = "places/{uuid}"
    search_map_details: str = "search"
    experiential_route: str = "experiential-route/{transport-mode}"


class STBResponseHandler(BaseResponseHandler):
    """Attempt to return the decoded response data as json."""

    @staticmethod
    def get_request_data(response: Response) -> OptionalJsonType:
        if response.get_raw_data() == "":
            return None

        try:
            response_json: OptionalJsonType = response.get_json()
        except JSONDecodeError as error:
            raise ResponseParseError(
                f"Unable to decode response data to json. data='{response.get_raw_data()}'"
            ) from error

        if response_json["status"]["name"] != "OK":
            raise APIClientError(response_json["message"])
        # check if attribute "data" exists
        if "data" not in response_json:
            return None
        return response_json


class DataframeResponseHandler(BaseResponseHandler):
    """Attempt to return the decoded response data as json."""

    @staticmethod
    def get_request_data(response: Response) -> DataFrame | None:
        if response.get_raw_data() == "":
            return None

        try:
            response_json: OptionalJsonType = response.get_json()
        except JSONDecodeError as error:
            raise ResponseParseError(
                f"Unable to decode response data to json. data='{response.get_raw_data()}'"
            ) from error

        if response_json["status"]["name"] != "OK":
            raise APIClientError(response_json["message"])
        # check if attribute "data" exists
        if "data" not in response_json:
            return None
        return json_normalize(response_json["data"])


class STBClient(BaseClient):
    """STB API client"""

    def __init__(
        self,
        authentication_method: Optional[
            BaseAuthenticationMethod
        ] = authentication_method,
        response_handler: Type[BaseResponseHandler] = STBResponseHandler,
        request_formatter: Type[BaseRequestFormatter] = JsonRequestFormatter,
        error_handler: Type[BaseErrorHandler] = ErrorHandler,
        request_strategy: Optional[BaseRequestStrategy] = None,
    ) -> None:
        """Initialize STB API client"""
        self.authentication_method = authentication_method
        self.endpoint = Endpoint
        self.mapendpoint = MapEndpoint
        super().__init__(
            authentication_method=self.authentication_method,
            response_handler=response_handler,
            request_formatter=request_formatter,
            error_handler=error_handler,
            request_strategy=request_strategy,
        )

    @paginated(by_query_params=get_next_page)
    @retry_request
    def get_accommodation(
        self, keyword: str, **kwargs: Unpack[Any]
    ) -> DataFrame | None:
        """Get accommodation from STB API"""
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response_json: Any = self.get(
            endpoint=self.endpoint.accommodation, params=params
        )

        # Concatenate the dataframes
        for page in response_json:
            if response_json.index(page) == 0:
                df = json_normalize(page["data"])
            else:
                df = concat([df, json_normalize(page["data"])], ignore_index=True)
        return df

    @paginated(by_query_params=get_next_page)
    @retry_request
    def get_attractions(self, keyword: str, **kwargs: Unpack[Any]) -> DataFrame | None:
        """Get accommodation from STB API"""
        if keyword == "":
            return None
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response_json: Any = self.get(endpoint=self.endpoint.attractions, params=params)
        # Concatenate the dataframes
        for page in response_json:
            if response_json.index(page) == 0:
                df = json_normalize(page["data"])
            else:
                df = concat([df, json_normalize(page["data"])], ignore_index=True)
        return df

    @retry_request
    def get_bar_clubs(self, keyword: str, **kwargs: Unpack[Any]) -> DataFrame | None:
        """Get bars and clubs from STB API"""
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response: Any = self.get(endpoint=self.endpoint.bars_clubs, params=params)

        return response

    @retry_request
    def get_cruises(self, keyword: str, **kwargs: Unpack[Any]) -> DataFrame | None:
        """Get cruises from STB API"""
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response: Any = self.get(endpoint=self.endpoint.cruises, params=params)

        return response

    @retry_request
    def get_events(self, keyword: str, **kwargs: Unpack[Any]) -> DataFrame | None:
        """Get events from STB API"""
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response: Any = self.get(endpoint=self.endpoint.events, params=params)

        return response

    @retry_request
    def get_food_beverages(
        self, keyword: str, **kwargs: Unpack[Any]
    ) -> DataFrame | None:
        """Get food and beverages from STB API"""
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response: Any = self.get(endpoint=self.endpoint.food_beverages, params=params)

        return response

    @retry_request
    def get_precincts(self, keyword: str, **kwargs: Unpack[Any]) -> DataFrame | None:
        """Get precincts from STB API"""
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response: Any = self.get(endpoint=self.endpoint.precincts, params=params)

        return response

    @retry_request
    def get_shops(self, keyword: str, **kwargs: Unpack[Any]) -> DataFrame | None:
        """Get shops from STB API"""
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response: Any = self.get(endpoint=self.endpoint.shops, params=params)

        return response

    @paginated(by_query_params=get_next_page)
    @retry_request
    def get_tours(self, keyword: str, **kwargs: Unpack[Any]) -> DataFrame | None:
        """Get tours from STB API"""
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response_json: Any = self.get(endpoint=self.endpoint.tours, params=params)

        # Concatenate the dataframes
        for page in response_json:
            if response_json.index(page) == 0:
                df = json_normalize(page["data"])
            else:
                df = concat([df, json_normalize(page["data"])], ignore_index=True)
        return df

    @paginated(by_query_params=get_next_page)
    @retry_request
    def get_venues(self, keyword: str, **kwargs: Unpack[Any]) -> DataFrame | None:
        """Get venues from STB API"""
        if keyword == "":
            return None
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response_json: Any = self.get(endpoint=self.endpoint.venues, params=params)

        # Concatenate the dataframes
        for page in response_json:
            if response_json.index(page) == 0:
                df = json_normalize(page["data"])
            else:
                df = concat([df, json_normalize(page["data"])], ignore_index=True)
        return df

    @retry_request
    def get_walking_trails(
        self, keyword: str, **kwargs: Unpack[Any]
    ) -> DataFrame | None:
        """Get walking trails from STB API"""
        params: Dict[str, str] = {"searchType": "keyword", "searchValues": keyword}
        params.update(kwargs)
        response: Any = self.get(endpoint=self.endpoint.walking_trails, params=params)

        return response

    @paginated(by_query_params=get_next_page)
    @retry_request
    def search_map_details(
        self, location: str, radius: int, **kwargs: Unpack[Any]
    ) -> DataFrame | None:
        """Search map details from STB API"""
        params: Dict[str, int] = {"location": location, "radius": radius}
        params.update(kwargs)
        response: Any = self.get(
            endpoint=self.mapendpoint.search_map_details, params=params
        )

        return response
