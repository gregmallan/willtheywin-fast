from fastapi import Depends, FastAPI, status, HTTPException


class HTTPExceptionNotFound(HTTPException):

    def __init__(self, detail):
        super().__init__(status_code=404, detail=detail)
