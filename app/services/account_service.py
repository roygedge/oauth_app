from typing import Dict, Any, Optional

from app.auth.token_repository import get_last_token
from app.clients.quickbooks_client import QuickBooksClient
from app.services.auth_service import AuthService
from app.decorators import quickbooks_api_wrapper

class AccountService:
    """Service for handling QuickBooks account operations."""

    def __init__(self, quickbooks_client: QuickBooksClient,
                  auth_service: AuthService):
        self.quickbooks_client = quickbooks_client
        self.auth_service = auth_service

    @quickbooks_api_wrapper
    def get_accounts(self, name_prefix: Optional[str] = None) -> Dict[str, Any]:
        """Get accounts from QuickBooks.
        
        Args:
            name_prefix: Optional prefix to filter account names
            
        Returns:
            Dict[str, Any]: A dictionary containing account information
        """
        token = get_last_token()
        return self.quickbooks_client.get_accounts(token, name_prefix)