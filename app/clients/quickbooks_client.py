import requests
from urllib.parse import urlencode
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.config import (
    QB_CLIENT_ID, QB_CLIENT_SECRET, QB_REDIRECT_URI,
    QB_AUTH_URL, QB_TOKEN_URL, QB_SCOPES, QB_BASE_URL
)
from app.models.token import Token

class QuickBooksClient:
    """Client for interacting with QuickBooks API."""
    
    def __init__(self):
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.qb_auth_credentials = (QB_CLIENT_ID, QB_CLIENT_SECRET)

    def construct_auth_url(self, state: str) -> str:
        """Construct the QuickBooks authorization URL.
        
        Args:
            state: A unique state parameter for security
            
        Returns:
            str: The complete authorization URL
        """
        params = {
            "client_id": QB_CLIENT_ID,
            "redirect_uri": QB_REDIRECT_URI,
            "response_type": "code",
            "scope": QB_SCOPES,
            "state": state,
        }
        return f"{QB_AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_tokens(self, code: str, realm_id: str) -> Token:
        """Exchange authorization code for access and refresh tokens.
        
        Args:
            code: The authorization code from QuickBooks
            realm_id: The QuickBooks realm ID
            
        Returns:
            Token: A new token instance with access and refresh tokens
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": QB_REDIRECT_URI,
        }
        token_data = self._make_token_request(data)
        return self._create_token(token_data, realm_id)

    def refresh_access_token(self, token: Token) -> Token:
        """Refresh an expired access token.
        
        Args:
            token: The token to refresh

        Returns:
            None
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        data = {
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
        }
        token_data = self._make_token_request(data)
        
        # Update existing token
        token.access_token = token_data["access_token"]
        token.expires_at = datetime.now() + timedelta(seconds=int(token_data["expires_in"]))
        token.updated_at = datetime.now()

    def get_accounts(self, token: Token, name_prefix: Optional[str] = None) -> Dict[str, Any]:
        """Get accounts from QuickBooks API.
        
        Args:
            token: The authentication token
            name_prefix: Optional filter for account names
            
        Returns:
            Dict[str, Any]: The API response containing account data
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        url = f"{QB_BASE_URL}/{token.realm_id}/query"
        query = "SELECT * FROM Account"
        if name_prefix:
            query += f" WHERE Name LIKE '{name_prefix}%'"
        
        headers = {
            "Authorization": f"Bearer {token.access_token}",
            "Accept": "application/json",
            "Content-Type": "text/plain"
        }
        
        response = requests.get(url, headers=headers, params={"query": query})
        response.raise_for_status()
        return response.json()

    def _make_token_request(self, data: Dict[str, str]) -> Dict[str, Any]:
        """Make a token request to QuickBooks API.
        
        Args:
            data: The request data for the token endpoint
            
        Returns:
            Dict[str, Any]: The API response containing token data
            
        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        response = requests.post(
            QB_TOKEN_URL,
            headers=self.headers,
            data=data,
            auth=self.qb_auth_credentials
        )
        response.raise_for_status()
        return response.json()

    def _create_token(self, token_data: Dict[str, Any], realm_id: str) -> Token:
        """Create a Token instance from API response data.
        
        Args:
            token_data: The token data from the API response
            realm_id: The QuickBooks realm ID
            
        Returns:
            Token: A new token instance
        """
        expires_in = int(token_data["expires_in"])
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        return Token(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            realm_id=realm_id,
            expires_at=expires_at
        ) 