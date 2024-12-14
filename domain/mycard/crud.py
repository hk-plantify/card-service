from sqlalchemy.orm import Session
from domain.mycard.models import MyCard, Card, Benefit
from domain.mycard.schemas import MyCardCreate, BenefitResponse, CardResponse
from collections import defaultdict
from sqlalchemy import or_
from rapidfuzz.fuzz import partial_ratio, token_sort_ratio, token_set_ratio
from fastapi import HTTPException

def create_mycard(db: Session, mycard: MyCardCreate, user_id: int):
    db_mycard = MyCard(card_id=mycard.card_id, user_id=user_id)
    db.add(db_mycard)
    db.commit()
    db.refresh(db_mycard)
    return db_mycard

def get_all_mycards(db: Session):
    return db.query(MyCard).all()

def delete_mycard(db: Session, mycard_id: int, user_id: int):
    db_mycard = db.query(MyCard).filter(
        MyCard.myCard_id == mycard_id, MyCard.user_id == user_id
    ).first()
    if not db_mycard:
        raise HTTPException(
            status_code=404,
            detail=f"Debug: MyCard not found. myCard_id={mycard_id}, user_id={user_id}"
        )
    db.delete(db_mycard)
    db.commit()
    return db_mycard

def get_card_with_benefits(db: Session, card_id: int):
    card = db.query(Card).filter(Card.card_id == card_id).first()
    if not card:
        return None
    # benefits에서 title만 추출
    benefits = db.query(Benefit).filter(Benefit.card_id == card_id).all()
    benefits_response = [benefit.title for benefit in benefits]

    card_response = CardResponse(
        card_id=card.card_id,
        name=card.name,
        image=card.image,
        company=card.company,
        type=card.type,
        benefits=benefits_response
    )
    return card_response

def calculate_similarity(query, text):
    return max(
        partial_ratio(query, text),
        token_sort_ratio(query, text),
        token_set_ratio(query, text)
    )

def search_cards(db: Session, query: str):
    # 방어적 쿼리 검사
    if not query or len(query.strip()) < 1:
        return []

    query = query.strip()

    # 데이터베이스에서 모든 카드 가져오기
    all_cards = db.query(Card).all()

    # 유사도 계산 및 랭킹
    ranked_cards = []
    for card in all_cards:
        name_similarity = calculate_similarity(query, card.name)
        company_similarity = calculate_similarity(query, card.company)
        score = max(name_similarity, company_similarity)

        # 이름 또는 회사 이름에 정확히 포함된 경우 가중치 추가
        if query.lower() in card.name.lower():
            score += 15
        if query.lower() in card.company.lower():
            score += 10

        ranked_cards.append((card, score))

    # 점수 순으로 정렬
    ranked_cards.sort(key=lambda x: x[1], reverse=True)

    # 최종 결과 반환
    return [card for card, _ in ranked_cards]
