from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from app.clients.quickbooks_client import QuickBooksClient
from app.database import Base, engine
from app.services.account_service import AccountService
from app.services.auth_service import AuthService
from app.services.session_service import SessionManager

# Drop all tables (for dev/testing only)
# Base.metadata.drop_all(bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI()

# Initialize session manager
session_manager = SessionManager()

# Initialize QuickBooks client
qb_client = QuickBooksClient()

# Initialize services
auth_service = AuthService(qb_client, session_manager)
account_service = AccountService(qb_client, auth_service)

@app.get("/login")
def login():
    state = session_manager.generate_state_parameter()
    return RedirectResponse(auth_service.get_auth_url(state))

@app.get("/callback")
def callback(request: Request):
    query_params = request.query_params
    return auth_service.handle_oauth_callback(
        code=query_params.get("code"),
        state=query_params.get("state"),
        realm_id=query_params.get("realmId")
    )

@app.get("/accounts")
def get_accounts(name_prefix: str = None):
    return account_service.get_accounts(name_prefix)

