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

mycard_router = APIRouter(prefix="/v1/mycards", tags=["MyCards"])

@mycard_router.post("", response_model=ApiResponse[MyCardResponse])
def create_mycard(
    mycard: MyCardCreate,
    db: Session = Depends(get_db),
    user: AuthUserResponse = Depends(validate_token),
):
    created_mycard = crud.create_mycard(db=db, mycard=mycard, user_id=user.userId)
    card = created_mycard.card

    card_response = CardResponse(
        card_id=card.card_id,
        name=card.name,
        image=card.image,
        company=card.company,
        type=card.type,
        benefits=[benefit.title for benefit in card.benefits]
    )
    response_data = MyCardResponse(
        id=created_mycard.myCard_id,
        card_id=created_mycard.card_id,
        card=card_response
    )
    return ApiResponse.ok(data=response_data)

@mycard_router.get("", response_model=ApiResponse[list[MyCardResponse]])
def get_all_mycards(db: Session = Depends(get_db)):
    mycards = crud.get_all_mycards(db=db)
    mycards_response = []

    for mycard in mycards:
        card_response = get_card_with_benefits(db=db, card_id=mycard.card_id)

        mycard_response = MyCardResponse(
            id=mycard.myCard_id,
            card_id=mycard.card_id,
            card=card_response
        )
        mycards_response.append(mycard_response)

    return ApiResponse.ok(data=mycards_response)

@mycard_router.delete("/{mycard_id}", response_model=ApiResponse[MyCardResponse])
def delete_mycard(
    mycard_id: int,  # 경로 변수 이름과 매개변수 이름 일치
    db: Session = Depends(get_db),
    user: AuthUserResponse = Depends(validate_token)
):
    mycard = crud.delete_mycard(db=db, mycard_id=mycard_id, user_id=user.userId)  # user_id 추가
    if not mycard:
        raise ApplicationException(status_code=404, detail="MyCard not found")
    return ApiResponse.ok(data=mycard)

@mycard_router.get("/healthz", response_model=ApiResponse[dict])
def health_check_mycards():
    return {"status": "ok", "service": "mycards"}

card_router = APIRouter(prefix="/v1/cards", tags=["Cards"])

@card_router.get("/search", response_model=ApiResponse[list[dict]])
def search_cards_api(
    query: str,
    db: Session = Depends(get_db),
):
    """
    검색된 카드와 함께 추가 가능 여부 반환.
    """
    # 검색된 카드 목록
    cards = search_cards(db=db, query=query)

    # 사용자가 이미 MyCards에 추가한 카드 목록
    user_mycards = crud.get_all_mycards(db=db)
    user_card_ids = {mycard.card_id for mycard in user_mycards}

    simplified_cards = []
    for card in cards:
        # 카드 정보에 addable 여부 추가
        simplified_cards.append({
            "name": card.name,
            "image": card.image,
            "company": card.company,
            "type": card.type,
            "card_id": card.card_id,
            "benefits": [benefit.title for benefit in card.benefits],
            "addable": card.card_id not in user_card_ids
        })

    return ApiResponse.ok(data=simplified_cards)

@card_router.get("/benefits/{cardId}", response_model=ApiResponse[CardResponse])
def get_card_with_benefits_api(
    cardId: int, 
    db: Session = Depends(get_db)
):
    card = get_card_with_benefits(db=db, card_id=cardId)
    if not card:
        raise ApplicationException(status_code=404, detail="Card not found")
    return ApiResponse.ok(data=card)

@card_router.get("/healthz", response_model=ApiResponse[dict])
def health_check_cards():
    return {"status": "ok", "service": "cards"}
