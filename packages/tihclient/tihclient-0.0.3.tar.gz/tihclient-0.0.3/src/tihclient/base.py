# Abstract class for a API client
"""Base class for API client"""

from typing import Type, Optional

from apiclient import (
    APIClient,
    JsonResponseHandler,
    JsonRequestFormatter,
)

from apiclient.authentication_methods import BaseAuthenticationMethod
from apiclient.response_handlers import BaseResponseHandler
from apiclient.request_formatters import BaseRequestFormatter
from apiclient.error_handlers import BaseErrorHandler, ErrorHandler
from apiclient.request_strategies import BaseRequestStrategy


class BaseClient(APIClient):
    """Base class for API client"""

    def __init__(
        self,
        authentication_method: Optional[BaseAuthenticationMethod] = None,
        response_handler: Type[BaseResponseHandler] = JsonResponseHandler,
        request_formatter: Type[BaseRequestFormatter] = JsonRequestFormatter,
        error_handler: Type[BaseErrorHandler] = ErrorHandler,
        request_strategy: Optional[BaseRequestStrategy] = None,
    ) -> None:
        super().__init__(
            authentication_method=authentication_method,
            response_handler=response_handler,
            request_formatter=request_formatter,
            error_handler=error_handler,
            request_strategy=request_strategy,
        )
