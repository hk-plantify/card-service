from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from domain.auth.oauth import validate_token
from domain.auth.schemas import AuthUserResponse
from domain.mycard import crud
from domain.mycard.schemas import MyCardCreate, MyCardResponse
from common.response.response import ApiResponse
from common.exception.exception import ApplicationException

router = APIRouter(prefix="/v1/mycards", tags=["MyCard"])

@router.post("", response_model=ApiResponse[MyCardResponse])
def create_mycard(
    mycard: MyCardCreate,
    db: Session = Depends(get_db),
    user: AuthUserResponse = Depends(validate_token),
):
    mycard.user_id = user.userId
    created_mycard = crud.create_mycard(db=db, mycard=mycard)
    return ApiResponse.ok(data=created_mycard)


@router.get("", response_model=ApiResponse[list[MyCardResponse]])
def get_all_mycards(
    db: Session = Depends(get_db),
    user: AuthUserResponse = Depends(validate_token)
):
    mycards = crud.get_all_mycards(db=db)
    return ApiResponse.ok(data=mycards)


@router.delete("/{mycardId}", response_model=ApiResponse[MyCardResponse])
def delete_mycard(
    mycard_id: int,
    db: Session = Depends(get_db),
    user: AuthUserResponse = Depends(validate_token)
):
    mycard = crud.delete_mycard(db=db, mycard_id=mycard_id)
    if not mycard:
        raise ApplicationException(status_code=404, detail="MyCard not found")
    return ApiResponse.ok(data=mycard)