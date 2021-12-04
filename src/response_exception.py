from fastapi import Depends, FastAPI, status, HTTPException


class HTTPBadRequest(HTTPException):
    def __init__(self, detail):
        super().__init__(status_code=400, detail=detail)


class HTTPExceptionNotFound(HTTPException):

    def __init__(self, detail):
        super().__init__(status_code=404, detail=detail)
