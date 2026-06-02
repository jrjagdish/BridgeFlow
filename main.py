from fastapi import FastAPI,HTTPException
from debug import logger
from oauth import get_authorize, exchange_code_for_tokens, get_valid_access_token
app = FastAPI()

@app.get("/")
def health_check():
    logger.info("Health check endpoint called.")
    return {"status": "ok"}

@app.post("/oauth/authorize")
def authorize():
    try:
        auth_url = get_authorize()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Error generating authorization URL: {e}")
        raise HTTPException(status_code=500, detail="Error generating authorization URL")

@app.get("/oauth/callback")
def oauth_callback(code: str):
    try:
        tokens = exchange_code_for_tokens(code)
        return {"message": "Authorization successful", "tokens": tokens}
    except Exception as e:
        logger.error(f"Error exchanging code for tokens: {e}")
        raise HTTPException(status_code=500, detail="Error exchanging code for tokens")