# data.py

from fastapi.responses import (
    RedirectResponse, Response, FileResponse,
    JSONResponse, HTMLResponse, StreamingResponse,
    PlainTextResponse, UJSONResponse, ORJSONResponse
)

__all__ = [
    "Responses",
    "GET",
    "POST",
    "DELETE",
    "UPLOAD",
    "HEAD",
    "PATCH",
    "PUT",
    "DOCS",
    "FAVICON",
    "METHODS",
    "EndpointRedirectResponse",
    "EndpointResponse",
    "EndpointFileResponse",
    "EndpointJSONResponse",
    "EndpointHTMLResponse",
    "EndpointStreamingResponse",
    "EndpointPlainTextResponse",
    "EndpointUJSONResponse",
    "EndpointORJSONResponse",
    "RESPONSES"
]

DOCS = '/docs'
FAVICON = '/favicon.ico'

class Methods:
    """A class to contain the methods of the service."""

    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    UPLOAD = "UPLOAD"
    HEAD = "HEAD"
    PATCH = "PATCH"
    PUT = "PUT"

    METHODS = (
        GET, POST, DELETE, UPLOAD,
        HEAD, PATCH, PUT
    )
# end Methods

GET = Methods.GET
POST = Methods.POST
DELETE = Methods.DELETE
UPLOAD = Methods.UPLOAD
HEAD = Methods.HEAD
PATCH = Methods.PATCH
PUT = Methods.PUT

METHODS = Methods.METHODS

class Responses:
    """A class to contain the response types."""

    EndpointRedirectResponse = RedirectResponse
    EndpointResponse = Response
    EndpointFileResponse = FileResponse
    EndpointJSONResponse = JSONResponse
    EndpointHTMLResponse = HTMLResponse
    EndpointStreamingResponse = StreamingResponse
    EndpointPlainTextResponse = PlainTextResponse
    EndpointUJSONResponse = UJSONResponse
    EndpointORJSONResponse = ORJSONResponse

    RESPONSES = (
        EndpointRedirectResponse, EndpointResponse,
        EndpointFileResponse, EndpointJSONResponse,
        EndpointHTMLResponse, EndpointStreamingResponse,
        EndpointPlainTextResponse, EndpointUJSONResponse,
        EndpointORJSONResponse
    )
# end Responses

EndpointRedirectResponse = Responses.EndpointRedirectResponse
EndpointResponse = Responses.EndpointResponse
EndpointFileResponse = Responses.EndpointFileResponse
EndpointJSONResponse = Responses.EndpointJSONResponse
EndpointHTMLResponse = Responses.EndpointHTMLResponse
EndpointStreamingResponse = Responses.EndpointStreamingResponse
EndpointPlainTextResponse = Responses.EndpointPlainTextResponse
EndpointUJSONResponse = Responses.EndpointUJSONResponse
EndpointORJSONResponse = Responses.EndpointORJSONResponse

RESPONSES = Responses.RESPONSES