import secrets

class SessionManager:
    """Manages session data for OAuth flow."""
    
    def __init__(self):
        """Initialize session manager."""
        self._session = {}  # Simple in-memory session store

    def generate_state_parameter(self) -> str:
        """Generate a random state parameter."""
        self._session["state"] = secrets.token_hex(16)
        return self._session["state"]

    def get(self, key: str):
        """Get a value from the session.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value if found, None otherwise
        """
        return self._session.get(key)