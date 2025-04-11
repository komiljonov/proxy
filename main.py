from fastapi import FastAPI, Request
from dotenv import load_dotenv
import httpx
import os
import logging

# Load environment variables from .env
load_dotenv()

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

app = FastAPI()

TARGET_DOMAIN = os.environ.get("TARGET_DOMAIN", "https://default-domain.com")


@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
async def proxy(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        # Build full URL
        url = f"{TARGET_DOMAIN.rstrip('/')}/{path}"
        if request.query_params:
            url += f"?{request.query_params}"
            
        logger.info(url)

        # Extract and log Token header
        headers = dict(request.headers)
        logger.info(headers)
        token = headers.get("token")
        logger.info(f"Proxying request to: {url}")
        logger.info(f"Using Token: {token}")

        # Read body
        body = await request.body()

        # Proxy the request
        proxied_response = await client.request(
            method=request.method,
            url=url,
            headers={"Token": token} if token else {},
            content=body,
            timeout=30.0,
        )

        # Try to return JSON, fallback to raw text
        try:
            return proxied_response.json()
        except Exception:
            return proxied_response.text
