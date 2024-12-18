from typing import List
from sqlalchemy.orm import Session

from common.exception.exception import ApplicationException, CardErrorCode
from domain.mycard.models import MyCard, Card, Benefit
from domain.mycard.schemas import MyCardCreate, BenefitResponse, CardResponse
from collections import defaultdict
from sqlalchemy import or_
from rapidfuzz.fuzz import partial_ratio, token_sort_ratio, token_set_ratio
from rapidfuzz import process


def create_mycards(db: Session, card_ids: List[int], user_id: int):
    db_mycards = []
    for card_id in card_ids:
        db_mycard = MyCard(card_id=card_id, user_id=user_id)
        db.add(db_mycard)
        db_mycards.append(db_mycard)
    db.commit()
    for db_mycard in db_mycards:
        db.refresh(db_mycard)
    return db_mycards

def get_all_mycards_by_user_id(db: Session, user_id: int):
    db_mycards = db.query(MyCard).filter(MyCard.user_id == user_id)

    if db_mycards.get("status") != 200 or "data" not in db_mycards:
        raise ApplicationException(*CardErrorCode.MYCARD_NOT_FOUND)

    return db.query(db_mycards).all()

def delete_mycard(db: Session, mycard_id: int, user_id: int):
    db_mycard = db.query(MyCard).filter(
        MyCard.myCard_id == mycard_id, MyCard.user_id == user_id
    ).first()

    if db_mycard.get("status") != 200 or "data" not in db_mycard:
        raise ApplicationException(*CardErrorCode.MYCARD_NOT_FOUND)

    db.delete(db_mycard)
    db.commit()
    return db_mycard

def get_card_with_benefits(db: Session, card_id: int):
    card = db.query(Card).filter(Card.card_id == card_id).first()

    if card.get("status") != 200 or "data" not in card:
        raise ApplicationException(*CardErrorCode.CARD_NOT_FOUND)

    # benefits에서 title만 추출
    benefits = db.query(Benefit).filter(Benefit.card_id == card_id).all()
    benefits_response = [benefit.title for benefit in benefits]

    card_response = CardResponse(
        card_id=card.card_id,
        card_name=card.name,
        card_image=card.image,
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

def correct_query(query, candidates, threshold=70):
    """
    검색어를 후보군과 비교하여 유사한 단어 리스트를 반환.
    """
    matches = process.extract(query, candidates, score_cutoff=threshold)
    return [match[0] for match in matches]  # 유사한 단어 리스트 반환

def search_cards(db: Session, query: str):
    if not query or len(query.strip()) < 1:
        return []

    query = query.strip()

    # 카드 이름과 회사 이름 후보군 가져오기
    card_names = [card.name for card in db.query(Card.name).distinct()]
    company_names = [card.company for card in db.query(Card.company).distinct()]
    candidates = card_names + company_names

    # 검색어 보정: threshold=70으로 설정
    corrected_queries = correct_query(query, candidates, threshold=70)

    # SQLAlchemy 필터링
    filters = [
        or_(
            Card.name.like(f"%{corrected_query}%"),  # LIKE 사용
            Card.company.like(f"%{corrected_query}%")  # LIKE 사용
        )
        for corrected_query in corrected_queries
    ]

    filtered_cards = db.query(Card).filter(or_(*filters)).limit(300).all()

    # Python에서 유사도 계산 및 랭킹
    ranked_cards = []
    for card in filtered_cards:
        name_similarity = calculate_similarity(query, card.name)
        company_similarity = calculate_similarity(query, card.company)
        score = max(name_similarity, company_similarity)

        # 이름 또는 회사 이름에 정확히 포함된 경우 가중치 추가
        if query.lower() in card.name.lower():
            score += 25
        if query.lower() in card.company.lower():
            score += 20

        ranked_cards.append((card, score))

    # 점수 순으로 정렬
    ranked_cards.sort(key=lambda x: x[1], reverse=True)

    # 최종 결과 반환
    return [card for card, _ in ranked_cards]