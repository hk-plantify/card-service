from sqlalchemy.orm import Session
from domain.mycard.models import MyCard, Card, Benefit
from domain.mycard.schemas import MyCardCreate

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
    # 카드 정보 쿼리
    card = db.query(Card).filter(Card.card_id == card_id).first()
    if card:
        # 혜택 정보 포함
        card.benefits = db.query(Benefit).filter(Benefit.card_id == card_id).all()
    return card

def search_cards(db: Session, query: str):
    return db.query(Card).filter(
        (Card.name.ilike(f"%{query}%")) | (Card.company_name.ilike(f"%{query}%"))
    ).all()
