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
    if len(query) < 3:
        return db.query(Card).filter(
            (Card.name.ilike(f"%{query}%")) | (Card.company.ilike(f"%{query}%"))
        ).all()
    
    query_trigrams = generate_trigrams(query)  # Trigram 생성

    filtered_cards = db.query(Card).filter(
        (Card.name.ilike(f"%{query}%")) | (Card.company.ilike(f"%{query}%"))
    ).all()

    trigram_matches = defaultdict(list)
    for card in filtered_cards:
        card_trigrams = generate_trigrams(card.name) | generate_trigrams(card.company)
        intersection = query_trigrams & card_trigrams  # Trigram 교집합 계산
        if intersection:
            trigram_matches[len(intersection)].append(card)

    sorted_candidates = [
        card for _, cards in sorted(trigram_matches.items(), key=lambda x: x[0], reverse=True)
        for card in cards
    ]

    ranked_cards = []
    for card in sorted_candidates:
        name_similarity = calculate_similarity_jellyfish(query, card.name)
        company_similarity = calculate_similarity_jellyfish(query, card.company)
        score = max(name_similarity, company_similarity)
        ranked_cards.append((card, score))

    ranked_cards.sort(key=lambda x: x[1], reverse=True)

    return [card for card, score in ranked_cards]