# My OAuth 2.0 Application

A FastAPI-based backend service that integrates with QuickBooks for account management and authentication.

## Features

- QuickBooks OAuth2 authentication
- Account management and listing
- PostgreSQL database integration
- Docker containerization

## Prerequisites

- Docker and Docker Compose
- Python 3.8 or higher (for local development)
- QuickBooks Developer account and credentials

## Running the Application

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd oauth_app
   ```

2. Start the services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

The application will be available at `http://localhost:8000`

### Local Development

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

- `GET /`: Health check endpoint
- `GET /login`: Initiates QuickBooks OAuth2 login flow
- `GET /callback`: OAuth2 callback endpoint
- `GET /accounts`: Lists QuickBooks accounts (optional name_prefix filter)

## Application Flow

1. **Authentication**
   - Visit `http://localhost:8000/login` in your browser
   - You will be redirected to QuickBooks login page
   - After successful login, QuickBooks will redirect you back to the callback URL

2. **Callback Processing**
   - The application processes the OAuth callback at `/callback`
   - Upon successful authentication, you'll see a success message
   - The application stores the access token securely in the database

3. **Accessing Accounts**
   - Once authenticated, you can access your QuickBooks accounts
   - View all accounts: `http://localhost:8000/accounts`
   - Filter accounts by name: `http://localhost:8000/accounts ?name_prefix=Bank`
   - The application automatically handles token refresh when needed

## Database

The application uses PostgreSQL as its database. The database is automatically set up when running with Docker Compose.

