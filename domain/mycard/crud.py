from sqlalchemy.orm import Session
from domain.mycard.models import MyCard, Card, Benefit
from domain.mycard.schemas import MyCardCreate, BenefitResponse, CardResponse

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
    benefits = db.query(Benefit).filter(Benefit.card_id == card_id).all()
    benefits_response = [BenefitResponse.from_orm(benefit) for benefit in benefits]

    card_response = CardResponse(
        card_id=card.card_id,
        name=card.name,
        image_url=card.image_url,
        company_name=card.company_name,
        card_type=card.card_type,
        benefits=benefits_response
    )
    return card_response


def search_cards(db: Session, query: str):
    return db.query(Card).filter(
        (Card.name.ilike(f"%{query}%")) | (Card.company_name.ilike(f"%{query}%"))
    ).all()
