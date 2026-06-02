import json
import os
from debug import logger
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

TOKENS_FILE = 'tokens.json'

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = "https://www.googleapis.com/auth/spreadsheets.readonly"

def get_authorize():
    """Authoaize using google credentials"""
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'response_type': 'code',
        'scope': SCOPES,
        'access_type': 'offline',
        'prompt': 'consent'
    }
    auth_url = requests.Request('GET', GOOGLE_AUTH_URL, params=params).prepare().url
    logger.info(f"Generated authorization URL: {auth_url}")
    return auth_url

def exchange_code_for_tokens(code):
    """Exchange the authorization code for access and refresh tokens."""
    response = requests.post(GOOGLE_TOKEN_URL, data={
        'code': code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        'grant_type': 'authorization_code'
    })
    response.raise_for_status()
    tokens = response.json()
    tokens['expires_at'] = (datetime.now() + timedelta(seconds=tokens['expires_in'])).isoformat()
    _save_tokens(tokens)
    logger.info("Exchanged authorization code for tokens and saved to file.")
    return tokens

def get_valid_access_token():
    """call before every api request to google sheet api"""
    tokens = _load_tokens()
    if not tokens:
        logger.warning("No tokens found. Please authenticate first.")
        raise RuntimeError("No tokens found. Please authenticate first.")
    expires_at = datetime.fromisoformat(tokens.get('expires_at', 0))
    if datetime.now() >= expires_at - timedelta(minutes=5):
        logger.info("Access token is expired or about to expire. Refreshing tokens.")
        tokens = refresh_access_token(tokens.get('refresh_token'))
    return tokens.get('access_token')

def refresh_access_token(refresh_token):
    """Refresh the access token using the refresh token."""
    response = requests.post(GOOGLE_TOKEN_URL, data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        'grant_type': 'refresh_token'
    })
    response.raise_for_status()
    tokens = response.json()
    tokens['refresh_token'] = refresh_token  # Keep the same refresh token
    tokens['expires_at'] = (datetime.now() + timedelta(seconds=tokens['expires_in'])).isoformat()
    _save_tokens(tokens)
    logger.info("Refreshed access token and saved to file.")
    return tokens

def _load_tokens():
    if not os.path.exists(TOKENS_FILE):
        logger.warning("Tokens file not found.")
        return None
    with open(TOKENS_FILE, 'r') as f:
        tokens = json.load(f)
    return tokens

def _save_tokens(tokens):
    with open(TOKENS_FILE, 'w') as f:
        json.dump(tokens, f,indent=4)