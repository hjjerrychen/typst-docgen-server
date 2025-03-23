from fastapi import HTTPException, Depends, status
from fastapi.security import APIKeyHeader
import secrets


class Auth:
    HEADER_PARSER = APIKeyHeader(name="X-API-KEY", auto_error=True)

    def __init__(self, api_key: str):
        self.api_key = api_key.encode("utf8")

    def verify_api_key(self, api_key: str) -> bool:
        return secrets.compare_digest(api_key.encode("utf8"), self.api_key)
