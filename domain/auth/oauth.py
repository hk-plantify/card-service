import httpx
from fastapi import Depends
from fastapi.security import HTTPBearer
from config.config import AUTH_SERVICE_URL
from domain.auth.schemas import AuthUserResponse
from common.exception.exception import ApplicationException, AuthErrorCode

oauth2_scheme = HTTPBearer()

def validate_token(token: str = Depends(oauth2_scheme)) -> AuthUserResponse:
    headers = {"Authorization": f"Bearer {token.credentials}"}
    try:
        with httpx.Client() as client:
            response = client.post(f"{AUTH_SERVICE_URL}/v1/auth/validate-token", headers=headers)
            response.raise_for_status()

        data = response.json()
        if data.get("status") != 200 or "data" not in data:
            raise ApplicationException(*AuthErrorCode.INVALID_TOKEN)

        return AuthUserResponse(**data["data"])
    except httpx.HTTPError:
        raise ApplicationException(*AuthErrorCode.AUTH_SERVICE_UNAVAILABLE)