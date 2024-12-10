from sqlalchemy.orm import Session
from domain.mycard.models import MyCard, Card, Benefit
from domain.mycard.schemas import MyCardCreate, BenefitResponse, CardResponse
import jellyfish
from collections import defaultdict

def create_mycard(db: Session, mycard: MyCardCreate):
    db_mycard = MyCard(**mycard.dict())
    db.add(db_mycard)
    db.commit()
    db.refresh(db_mycard)
    return db_mycard

def get_all_mycards(db: Session):
    return db.query(MyCard).all()

def delete_mycard(db: Session, mycard_id: int):
    db_mycard = db.query(MyCard).filter(MyCard.myCard_id == mycard_id).first()
    if db_mycard:
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

def generate_trigrams(text):
    text = text.lower()
    return {text[i:i+3] for i in range(len(text) - 2)}

def calculate_similarity_jellyfish(query, text):
    distance = jellyfish.damerau_levenshtein_distance(query.lower(), text.lower())
    max_len = max(len(query), len(text))
    similarity = (1 - distance / max_len) * 100 
    return similarity

def search_cards(db: Session, query: str):
    # 짧은 쿼리는 간단한 필터로 처리
    if len(query) < 3:
        return db.query(Card).filter(
            (Card.name.ilike(f"%{query}%")) | (Card.company.ilike(f"%{query}%"))
        ).limit(100).all()  # 제한 추가

    query_trigrams = generate_trigrams(query)

    # 데이터베이스에서 초기 필터링
    filtered_cards = db.query(Card).filter(
        (Card.name.ilike(f"%{query}%")) | (Card.company.ilike(f"%{query}%"))
    ).limit(100).all()  # 초기 결과를 제한

    # 정확히 포함된 결과를 우선 수집
    exact_matches = [
        card for card in filtered_cards
        if query in card.name or query in card.company
    ]

    # 트라이그램 기반 매칭
    trigram_matches = defaultdict(list)
    for card in filtered_cards:
        card_trigrams = generate_trigrams(card.name) | generate_trigrams(card.company)
        intersection = query_trigrams & card_trigrams
        if intersection:
            trigram_matches[len(intersection)].append(card)

    # 트라이그램 교집합 크기에 따라 정렬
    sorted_candidates = [
        card for _, cards in sorted(trigram_matches.items(), key=lambda x: x[0], reverse=True)
        for card in cards
    ]

    # 유사도 계산 및 랭킹
    ranked_cards = []
    for card in sorted_candidates:
        name_similarity = calculate_similarity_jellyfish(query, card.name)
        company_similarity = calculate_similarity_jellyfish(query, card.company)
        score = max(name_similarity, company_similarity)
        if query in card.name:
            score += 10  # 이름에 정확히 포함된 경우 가중치 부여
        if query in card.company:
            score += 10  # 회사 이름에 정확히 포함된 경우 가중치 부여
        ranked_cards.append((card, score))

    ranked_cards.sort(key=lambda x: x[1], reverse=True)

    # 최종 결과 병합
    seen = set()
    final_result = []

    for card in exact_matches:
        if card not in seen:
            final_result.append(card)
            seen.add(card)

    for card, _ in ranked_cards:
        if card not in seen:
            final_result.append(card)
            seen.add(card)

    return final_result
