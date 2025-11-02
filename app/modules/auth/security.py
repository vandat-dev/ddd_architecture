import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Union, List
from urllib.parse import urlparse

import httpx
import jwt
import requests
from fastapi import Response, Request
from jwt import PyJWKClient

from app.core.app_status import AppStatus
from app.core.setting import settings
from app.utils.response import error_exception_handler

logger = logging.getLogger(__name__)


class TokenService:
    def __init__(self):
        self.keycloak_url = settings.KEYCLOAK_URL
        self.keycloak_realm = settings.KEYCLOAK_REALM
        self.keycloak_client_id = settings.KEYCLOAK_CLIENT_ID
        self.keycloak_client_secret = settings.KEYCLOAK_CLIENT_SECRET
        self.keycloak_redirect_url = settings.KEYCLOAK_REDIRECT_URL
        self.token_url = f"{self.keycloak_url}/realms/{self.keycloak_realm}/protocol/openid-connect/token"
        self.jwks_url = f"{self.keycloak_url}/realms/{self.keycloak_realm}/protocol/openid-connect/certs"
        self.jwk_client = PyJWKClient(self.jwks_url)

    async def generate_refresh_tokens(self, refresh_token: str):
        """Use refresh_token for get access_token + refresh_token new"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.token_url,
                data={
                    "grant_type": "refresh_token",
                    "client_id": self.keycloak_client_id,
                    "client_secret": self.keycloak_client_secret,
                    "refresh_token": refresh_token,
                },
            )
        if resp.status_code != 200:
            logger.error(f"Keycloak refresh token failed: {resp.status_code} - {resp.text}")
            return None
        return resp.json()

    async def exchange_code_for_token(self, code: str):
        """Đổi authorization code lấy access + refresh token"""
        async with httpx.AsyncClient() as client:
            token_url = f"{self.keycloak_url}/realms/{self.keycloak_realm}/protocol/openid-connect/token"
            resp = requests.post(
                token_url,
                data={
                    "client_id": self.keycloak_client_id,
                    "client_secret": self.keycloak_client_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.keycloak_redirect_url,
                },
            )
            if resp.status_code != 200:
                raise error_exception_handler(AppStatus.UNAUTHORIZED)
            return resp.json()

    def validate_token(self, token: str) -> Union[Dict[str, Any], None]:
        """
        Validate a given token (access or refresh).

        Args:
            token (str): The token to validate.

        Returns:
            dict | None: Decoded token payload if valid; None if invalid or expired.
        """
        try:
            signing_key = self.jwk_client.get_signing_key_from_jwt(token)
            decoded = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],
                options={
                    "verify_exp": True,
                    "verify_aud": False
                },
            )
            return decoded
        except jwt.ExpiredSignatureError:
            logger.warning("TokenService.validate_token - Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.error("TokenService.validate_token - Token is invalid")
            return None


class CookieService:

    @staticmethod
    def get_cookie(request: Request) -> dict:
        token = request.cookies
        return token

    @staticmethod
    def clear_cookie(response: Response):
        response.delete_cookie(key="access_token", samesite='none', httponly=True, secure=True)
        response.delete_cookie(key="refresh_token", samesite='none', httponly=True, secure=True)

    @staticmethod
    def get_token_from_cookie(cookie_name: str, request: Request) -> Union[str, None]:
        """
        Get a token from the request cookies.

        Args:
            cookie_name (str): The name of the cookie to retrieve.
            request (Request): The FastAPI Request object.

        Returns:
            str | None: The value of the cookie if it exists, None otherwise.
        """
        token = request.cookies.get(cookie_name, None)
        return token

    @staticmethod
    def get_origin_from_request(request: Request) -> str:
        """
        Extract the origin from the request using the Origin or Referer headers.
        If both are missing, fall back to a trusted default.

        Returns:
            str: Origin in the format "scheme://host[:port]"
        """
        # 1. Ưu tiên Origin
        origin = request.headers.get("origin")
        if origin:
            return origin

        referer = request.headers.get("referer")
        if referer:
            parsed = urlparse(referer)
            origin = f"{parsed.scheme}://{parsed.hostname}"
            if parsed.port:
                origin += f":{parsed.port}"
            return origin

        fallback_origin = settings.ALLOW_ORIGINS.split(",")[0]
        return fallback_origin

    @staticmethod
    def is_allowed_origin(origin: str, allowed_origins: List[str]) -> bool:
        """
        Check if the request origin is in the list of allowed origins.

        Args:
            origin (str): The request origin.
            allowed_origins (list): List of allowed hosts.

        Returns:
            bool: True if the origin is allowed, False otherwise.
        """
        return origin in allowed_origins or "*" in allowed_origins

    @staticmethod
    def set_cookie(response: Response, key: str, value: str, request_origin: str,
                   max_age: timedelta = timedelta(hours=1)):
        """
        Set a cookie dynamically based on the allowed origins (hosts).

        Args:
            response (Response): FastAPI Response object to set the cookie on.
            key (str): The cookie name.
            value (str): The cookie value.
            request_origin (str): The origin of the incoming request.
            max_age (int): Lifetime of the cookie in seconds (default: 3600 = 1 hour).
        """
        if CookieService.is_allowed_origin(request_origin, settings.ALLOW_ORIGINS):
            print(datetime.now(timezone.utc) + max_age)
            response.set_cookie(
                key=key,
                value=value,
                httponly=True,
                secure=True,
                samesite='none',
                expires=datetime.now(timezone.utc) + max_age

            )
        else:
            raise error_exception_handler(AppStatus.FORBIDDEN)
