from fastapi import HTTPException, status

from app.models.token import Token
from app.auth.token_repository import add_token_to_db, commit_db
from app.clients.quickbooks_client import QuickBooksClient
from app.services.session_service import SessionManager
from app.decorators import auth_endpoint_wrapper

class AuthService:
    def __init__(self, qb_client: QuickBooksClient,
                  session: SessionManager):
        self.session = session
        self.quickbooks_client = qb_client

    def validate_state_parameter(self, state: str) -> None:
        """Validate the state parameter against stored state."""
        if not state or state != self.session.get("state"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )
        
    def get_auth_url(self, state: str) -> str:
        """Get the QuickBooks authorization URL.
        
        Args:
            state: A unique state parameter for security
            
        Returns:
            str: The complete authorization URL
        """
        return self.quickbooks_client.construct_auth_url(state)

    @auth_endpoint_wrapper
    def handle_oauth_callback(self, code: str, state: str, realm_id: str) -> dict:
        """Handle OAuth callback and return authentication result.
        
        Args:
            code: The authorization code from QuickBooks
            state: The state parameter from the initial request
            realm_id: The QuickBooks realm ID

        Returns:
            dict: Authentication result containing success message
        """
        self.validate_state_parameter(state)
        token = self.quickbooks_client.exchange_code_for_tokens(code, realm_id)
        add_token_to_db(token)
        return {
            "msg": "Authentication successful, now you can access your accounts."
        }
    
    @auth_endpoint_wrapper
    def refresh_token(self, token: Token) -> Token:
        """Refresh an expired token.
        
        Args:
            token: The token to refresh
        """
        self.quickbooks_client.refresh_access_token(token)
        commit_db()