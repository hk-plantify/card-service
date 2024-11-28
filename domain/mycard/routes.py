from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from domain.auth.oauth import validate_token
from domain.auth.schemas import AuthUserResponse
from domain.mycard import crud
from domain.mycard.schemas import MyCardCreate, MyCardResponse, CardResponse
from domain.mycard.crud import get_card_with_benefits, search_cards
from common.response.response import ApiResponse
from common.exception.exception import ApplicationException
from urllib.parse import unquote

mycard_router = APIRouter(prefix="/v1/mycards", tags=["MyCards"])

@mycard_router.post("", response_model=ApiResponse[MyCardResponse])
def create_mycard(
    mycard: MyCardCreate,
    db: Session = Depends(get_db),
    user: AuthUserResponse = Depends(validate_token),
):
    mycard.user_id = user.userId
    created_mycard = crud.create_mycard(db=db, mycard=mycard)
    return ApiResponse.ok(data=created_mycard)

@mycard_router.get("", response_model=ApiResponse[list[MyCardResponse]])
def get_all_mycards(
    db: Session = Depends(get_db),
    user: AuthUserResponse = Depends(validate_token),
):
    mycards = crud.get_all_mycards(db=db)
    for mycard in mycards:
        mycard.card = get_card_with_benefits(db=db, card_id=mycard.card_id)
    return ApiResponse.ok(data=mycards)


@mycard_router.delete("/{mycardId}", response_model=ApiResponse[MyCardResponse])
def delete_mycard(
    mycard_id: int,
    db: Session = Depends(get_db),
    user: AuthUserResponse = Depends(validate_token)
):
    mycard = crud.delete_mycard(db=db, mycard_id=mycard_id)
    if not mycard:
        raise ApplicationException(status_code=404, detail="MyCard not found")
    return ApiResponse.ok(data=mycard)

card_router  = APIRouter(prefix="/v1/cards", tags=["Cards"])

@card_router.get("/search", response_model=ApiResponse[list[CardResponse]])
def search_cards_api(
    query: str,
    db: Session = Depends(get_db),
):
    print(f"Query received: {query}")
    cards = search_cards(db=db, query=query)
    return ApiResponse.ok(data=cards)

@card_router.get("/benefits/{cardId}", response_model=ApiResponse[CardResponse])
def get_card_with_benefits_api(
    cardId: int, 
    db: Session = Depends(get_db)
):
    card = get_card_with_benefits(db=db, card_id=cardId)
    if not card:
        raise ApplicationException(status_code=404, detail="Card not found")
    return ApiResponse.ok(data=card)