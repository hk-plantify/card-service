from sqlalchemy.orm import Session
from domain.mycard.models import MyCard
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