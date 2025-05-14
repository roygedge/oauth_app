import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:mypassword@db:5432/auth")
QB_CLIENT_ID: str = os.getenv("QB_CLIENT_ID", "")
QB_CLIENT_SECRET: str = os.getenv("QB_CLIENT_SECRET", "")
QB_SCOPES: str = "com.intuit.quickbooks.accounting"
QB_AUTH_URL: str = f"https://appcenter.intuit.com/connect/oauth2"
QB_TOKEN_URL: str = f"https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
QB_BASE_URL: str = f"https://sandbox-quickbooks.api.intuit.com/v3/company"
QB_REDIRECT_URI: str = "http://localhost:8000/callback"


