import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any

import httpx

from app.core.app_status import AppStatus
from app.modules.auth.security import TokenService
from app.utils.response import error_exception_handler
from app.core.setting import settings

logger = logging.getLogger(__name__)


class KeycloakAdminService:
    """
    Manages Keycloak Admin API interactions using a client service account.

    This service handles automated token acquisition/caching and provides
    methods for user management (e.g., creating users).
    It uses a persistent httpx.AsyncClient for connection pooling.
    """

    def __init__(self):
        """Initializes the service with Keycloak configuration."""
        self.keycloak_url = settings.KEYCLOAK_URL
        self.realm = settings.KEYCLOAK_REALM
        self.client_id = settings.KEYCLOAK_CLIENT_ID
        self.client_secret = settings.KEYCLOAK_CLIENT_SECRET

        self.admin_api_url = f"{self.keycloak_url}/admin/realms/{self.realm}"
        self.token_url = f"{self.keycloak_url}/realms/{self.realm}/protocol/openid-connect/token"

        # Token caching
        self._admin_token: Optional[str] = None
        self._token_expires_at: datetime = datetime.now(timezone.utc)

        # Use a persistent client for connection pooling
        self.http_client = httpx.AsyncClient()

    async def close(self):
        """Closes the persistent HTTP client. Should be called on app shutdown."""
        await self.http_client.aclose()

    async def _get_admin_token(self) -> str:
        """
        Retrieves a valid service account token, using cache if available.

        Returns:
            A valid admin access token.

        Raises:
            HTTPException: If token retrieval fails.
        """
        # Check cache, leaving a 60-second buffer for network latency
        if self._admin_token and self._token_expires_at > (datetime.now(timezone.utc) + timedelta(seconds=60)):
            return self._admin_token

        logger.info("Fetching new Keycloak admin token for service account...")
        try:
            response = await self.http_client.post(
                self.token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }
            )

            # Raise exception for 4xx/5xx responses
            response.raise_for_status()

            token_data = response.json()
            self._admin_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 300)  # Default 5 mins
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

            logger.info("Successfully fetched new Keycloak admin token.")
            return self._admin_token

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get admin token: {e.response.status_code} - {e.response.text}")
            raise error_exception_handler(AppStatus.ERROR_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An unexpected error occurred during token fetch: {e}")
            self._admin_token = None  # Reset cache on unknown error
            raise error_exception_handler(AppStatus.ERROR_INTERNAL_SERVER_ERROR)

    async def _make_admin_api_request(self, method: str, endpoint: str, **kwargs: Any) -> httpx.Response:
        """
        A generic helper to make authenticated requests to the Keycloak Admin API.
        It handles token acquisition, auth headers, and base error handling.

        Args:
            method: HTTP method (e.g., "POST", "GET", "DELETE").
            endpoint: API endpoint (e.g., "users", "users/{id}").
            **kwargs: Other arguments to pass to httpx.request (e.g., json, params).

        Returns:
            The httpx.Response object.

        Raises:
            httpx.HTTPStatusError: If the API returns a 4xx or 5xx status.
        """
        token = await self._get_admin_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            **(kwargs.pop("headers", {}))  # Allow overriding headers
        }

        try:
            response = await self.http_client.request(
                method=method,
                url=f"{self.admin_api_url}/{endpoint}",
                headers=headers,
                **kwargs
            )

            # Raise an exception for 4xx/5xx responses
            response.raise_for_status()
            return response

        except httpx.HTTPStatusError as e:
            # If auth failed (401/403), clear the token cache for a retry next time
            if e.response.status_code in [401, 403]:
                logger.warning(f"Admin API request failed ({e.response.status_code}). Clearing token cache.")
                self._admin_token = None
            # Re-raise the exception for the calling function to handle
            raise e

    @staticmethod
    def _build_user_payload(user_data: Dict) -> Dict:
        """
        Builds the Keycloak user representation from the application's user data.
        This isolates the data mapping logic.

        Args:
            user_data: The application's user data dictionary.

        Returns:
            A dictionary formatted for the Keycloak Admin API.
        """
        return {
            "username": user_data["username"],
            "email": user_data["email"],
            "enabled": True,
            "emailVerified": True,
            "credentials": [{
                "type": "password",
                "value": user_data["password"],
                "temporary": False
            }]
        }

    @staticmethod
    def _extract_user_id_from_location(response: httpx.Response) -> str:
        """
        Parses the 'Location' header from a 201 Created response.

        Args:
            response: The successful httpx.Response object.

        Returns:
            The extracted user ID.

        Raises:
            HTTPException: If the Location header is missing.
        """
        location_header = response.headers.get("Location")
        if not location_header:
            logger.error("No 'Location' header in Keycloak response after user creation")
            raise error_exception_handler(AppStatus.ERROR_INTERNAL_SERVER_ERROR)

        return location_header.split("/")[-1]

    async def create_user(self, user_data: Dict) -> str:
        """
        Creates a new user in Keycloak.
        This method now orchestrates other helper methods.

        Args:
            user_data: A dictionary with user info (username, email, password, fullname).

        Returns:
            The new user's Keycloak ID (sub).

        Raises:
            HTTPException: If the user already exists (409),
                            data is invalid (400),
                            or another API error occurs.
        """
        payload = self._build_user_payload(user_data)

        try:
            response = await self._make_admin_api_request(
                method="POST",
                endpoint="users",
                json=payload
            )

            user_id = self._extract_user_id_from_location(response)
            logger.info(f"Successfully created user in Keycloak with sub (id): {user_id}")
            return user_id

        except httpx.HTTPStatusError as e:
            # Now we only handle application-specific error translation here
            if e.response.status_code == 409:
                logger.warning(f"User creation failed: Conflict. {e.response.text}")
                raise error_exception_handler(AppStatus.ERROR_USER_ALREADY_EXISTS)
            elif e.response.status_code == 400:
                logger.warning(f"User creation failed: Bad Request. {e.response.text}")
                raise error_exception_handler(AppStatus.BAD_REQUEST)
            else:
                logger.error(f"Failed to create user in Keycloak: {e.response.status_code} - {e.response.text}")
                raise error_exception_handler(AppStatus.ERROR_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"An unexpected error occurred during user creation: {str(e)}")
            raise error_exception_handler(AppStatus.ERROR_INTERNAL_SERVER_ERROR)