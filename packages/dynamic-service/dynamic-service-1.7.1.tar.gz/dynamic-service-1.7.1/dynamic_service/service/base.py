# base.py

from typing import (
    Optional, Union, Dict, Any, Iterable
)

from dynamic_service.endpoints import (
    BaseEndpoint, valid_endpoints
)

__all__ = [
    "EndpointsService"
]

Endpoints = Dict[str, BaseEndpoint]
EndpointsContainer = Union[Iterable[BaseEndpoint], Endpoints]

class EndpointsService:
    """A class to represent an endpoints service."""

    def __init__(
            self,
            endpoints: Optional[EndpointsContainer] = None
    ) -> None:
        """
        Defines the server datasets for clients and client commands.

        :param endpoints: The commands to run for specific requests of the clients.
        """

        self.endpoints = self.valid_endpoints(endpoints or {})

        for endpoint in self.endpoints.values():
            endpoint.service = self
        # end for
    # end __init__

    @staticmethod
    def valid_endpoints(endpoints: Optional[Any] = None) -> Endpoints:
        """
        Process the endpoints' commands to validate and modify it.

        :param endpoints: The endpoints object to check.

        :return: The valid endpoints object.
        """

        return valid_endpoints(endpoints=endpoints)
    # end valid_endpoints

    def add_endpoint(self, endpoint: BaseEndpoint, path: Optional[str] = None) -> None:
        """
        Adds the endpoint to the service.

        :param path: The path for the endpoint.
        :param endpoint: The command to run.
        """

        self.endpoints[path or endpoint.path] = endpoint
    # end add_endpoint

    def add_endpoints(self, endpoints: EndpointsContainer) -> None:
        """
        Adds the endpoint to the service.

        :param endpoints: The commands to run.
        """

        self.endpoints.update(self.valid_endpoints(endpoints))
    # end add_endpoints

    def set_endpoint(
            self, endpoint: BaseEndpoint, path: Optional[str] = None
    ) -> None:
        """
        Adds the endpoint to the service.

        :param path: The path for the endpoint.
        :param endpoint: The command to run.
        """

        path = path or endpoint.path

        if path not in self.endpoints:
            raise ValueError(
                f"The path was not initialized for a different "
                f"endpoint beforehand. Consider using "
                f"'{self.add_endpoint.__name__}' method instead, "
                f"to add endpoints with new path. Given path: {path}. "
                f"Valid paths: {', '.join(self.endpoints.keys())}"
            )
        # end if

        self.endpoints[path] = endpoint
    # end set_endpoint

    def remove_endpoint(
            self, *,
            path: Optional[str] = None,
            endpoint: Optional[BaseEndpoint] = None
    ) -> None:
        """
        Removes the endpoint from the service.

        :param path: The index for the endpoint.
        :param endpoint: The command to run.
        """

        if path is not None:
            try:
                self.endpoints.pop(path)

            except KeyError:
                raise ValueError(
                    f"The path was not initialized for a different "
                    f"endpoint beforehand, therefore an endpoint "
                    f"labeled with that path couldn't be removed. Given path: {path}. "
                    f"Valid paths: {', '.join(self.endpoints.keys())}"
                )
            # end try

        elif endpoint is not None:
            for key, value in self.endpoints.items():
                if (value is endpoint) or (value == endpoint):
                    self.endpoints.pop(key)
                # end if

            else:
                raise ValueError(
                    f"Endpoint object '{repr(endpoint)}' doesn't "
                    f"exist in the endpoints of service object {repr(self)}, "
                    f"therefore could not be removed. Given path: {path}. "
                    f"Valid paths: {', '.join(self.endpoints.keys())}"
                )
            # end for
        # end if
    # end remove_endpoint

    def remove_endpoints(
            self, *,
            paths: Optional[Iterable[str]] = None,
            endpoints: Optional[EndpointsContainer] = None
    ) -> None:
        """
        Removes the endpoint from the service.

        :param paths: The paths for the endpoint.
        :param endpoints: The commands to run.
        """

        if paths is not None:
            for path in paths:
                self.remove_endpoint(path=path)
            # end if

        else:
            for endpoint in endpoints:
                self.remove_endpoint(endpoint=endpoint)
            # end for
        # end if
    # end remove_endpoint

    def remove_all_endpoints(self) -> None:
        """Removes all the endpoints from the service."""

        self.endpoints.clear()
    # end remove_all_endpoints

    def update_endpoints(self, endpoints: EndpointsContainer) -> None:
        """
        Adds the endpoint to the service.

        :param endpoints: The commands to run.
        """

        self.endpoints.update(self.valid_endpoints(endpoints))
    # end update_endpoints
# end EndpointsService