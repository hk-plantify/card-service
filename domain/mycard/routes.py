from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from domain.auth.oauth import validate_token
from domain.auth.schemas import AuthUserResponse
from domain.mycard import crud
from domain.mycard.schemas import MyCardResponse, CardResponse
from domain.mycard.crud import get_card_with_benefits, search_cards
from common.response.response import ApiResponse
from common.exception.exception import ApplicationException

mycard_router = APIRouter(prefix="/v1/mycards", tags=["MyCards"])

@mycard_router.post("", response_model=ApiResponse[List[MyCardResponse]])
def create_mycard(
    mycards: List[int],
    db: Session = Depends(get_db),
    user: AuthUserResponse = Depends(validate_token),
):
    created_mycards = crud.create_mycards(db=db, card_ids=mycards, user_id=user.userId)
    response_data = []

    for created_mycard in created_mycards:
        card = created_mycard.card

        card_response = CardResponse(
            card_id=card.card_id,
            card_name=card.name,
            card_image=card.image,
            company=card.company,
            type=card.type,
            benefits=[benefit.title for benefit in card.benefits],
        )
        response_data.append(
            MyCardResponse(
                myCard_id=created_mycard.myCard_id,
                card_id=created_mycard.card_id,
                card=card_response,
            )
        )

    return ApiResponse.ok(data=response_data)

@mycard_router.get("", response_model=ApiResponse[list[MyCardResponse]])
def get_all_mycards(
        db: Session = Depends(get_db),
        user: AuthUserResponse = Depends(validate_token)
):
    mycards = crud.get_all_mycards_by_user_id(db=db, user_id=user.userId)
    mycards_response = []

    for mycard in mycards:
        card_response = get_card_with_benefits(db=db, card_id=mycard.card_id)

        mycard_response = MyCardResponse(
            myCard_id=mycard.myCard_id,
            card_id=mycard.card_id,
            card=card_response
        )
        mycards_response.append(mycard_response)

    return ApiResponse.ok(data=mycards_response)

@mycard_router.delete("/{myCard_id}", response_model=ApiResponse[MyCardResponse])
def delete_mycard(
    myCard_id: int,
    db: Session = Depends(get_db),
    user: AuthUserResponse = Depends(validate_token)
):
    # MyCard 삭제
    mycard = crud.delete_mycard(db=db, mycard_id=myCard_id, user_id=user.userId)

    # Card 데이터 직렬화
    response_data = MyCardResponse(
        myCard_id=mycard.myCard_id,
        card_id=mycard.card_id,
        card=CardResponse(
            card_id=mycard.card.card_id,
            card_name=mycard.card.name,
            card_image=mycard.card.image,
            company=mycard.card.company,
            type=mycard.card.type,
            benefits=[benefit.title for benefit in mycard.card.benefits]  # 변환
        )
    )
    return ApiResponse.ok(data=response_data)

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
    user_mycards = crud.get_all_mycards_by_user_id(db=db)
    user_card_ids = {mycard.card_id for mycard in user_mycards}

    simplified_cards = []
    for card in cards:
        # 카드 정보에 addable 여부 추가
        simplified_cards.append({
            "card_name": card.name,
            "card_image": card.image,
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