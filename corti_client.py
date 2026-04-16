"""
Corti API Client - Handles authentication and API communication
"""
import os
import requests
from typing import Dict, Optional


class CortiClient:
    """Client for authenticating and interacting with Corti API"""

    def __init__(self):
        """Initialize client with credentials from environment variables"""
        self.tenant_name = os.getenv("CORTI_TENANT_NAME")
        self.client_id = os.getenv("CORTI_CLIENT_ID")
        self.client_secret = os.getenv("CORTI_CLIENT_SECRET")
        self.environment = os.getenv("CORTI_ENVIRONMENT", "eu")

        # Validate credentials
        if not all([self.tenant_name, self.client_id, self.client_secret]):
            raise ValueError("Missing credentials. Check your .env file.")

        # Set API URLs
        self.auth_url = f"https://auth.{self.environment}.corti.app/realms/{self.tenant_name}/protocol/openid-connect/token"
        self.api_url = f"https://api.{self.environment}.corti.app/v2"

        # Token will be set after authentication
        self.access_token: Optional[str] = None

    def authenticate(self) -> str:
        """
        Authenticate with Corti API and get access token

        Returns:
            Access token string
        """
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(self.auth_url, data=payload, timeout=10)
            response.raise_for_status()
            self.access_token = response.json().get("access_token")
            return self.access_token
        except requests.exceptions.RequestException as e:
            raise Exception(f"Authentication failed: {e}")

    def get_headers(self, include_tenant: bool = True) -> Dict[str, str]:
        """
        Generate headers for API requests

        Args:
            include_tenant: Whether to include Tenant-Name header

        Returns:
            Dictionary of headers
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        if include_tenant:
            headers["Tenant-Name"] = self.tenant_name

        return headers
