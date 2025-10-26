from fastapi import APIRouter, Depends
from domain.auth.schemas import AuthUserResponse
from oauth import validate_token
from common.response.response import ApiResponse

router = APIRouter(prefix="/v1/auth", tags=["Auth"])

@router.post("/validate-token", response_model=ApiResponse[AuthUserResponse])
def validate_user(user: AuthUserResponse = Depends(validate_token)):
    return ApiResponse.ok(data=user)