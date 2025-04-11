from fastapi import FastAPI, Request
from dotenv import load_dotenv
import httpx
import os

load_dotenv()

app = FastAPI()

TARGET_DOMAIN = os.environ.get("TARGET_DOMAIN", "https://default-domain.com")  # fallback optional

@app.api_route(
    "/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
async def proxy(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        # Build full URL
        url = f"{TARGET_DOMAIN.rstrip('/')}/{path}"
        if request.query_params:
            url += f"?{request.query_params}"

        # Prepare headers
        headers = dict(request.headers)
        token = headers.get('Token')

        # Read body
        body = await request.body()

        # Proxy the request
        proxied_response = await client.request(
            method=request.method,
            url=url,
            headers={
                "Token": token
            },
            content=body,
            timeout=30.0,
        )

        return proxied_response.json()