from sqlalchemy.orm import Session
from database import models, schemas

def create_mycard(db: Session, mycard: schemas.MyCardCreate):
    db_mycard = models.MyCard(**mycard.dict())
    db.add(db_mycard)
    db.commit()
    db.refresh(db_mycard)

    return db_mycard

def get_all_mycards(db: Session):
    return db.query(models.MyCard).all()


def delete_mycard(db: Session, mycard_id: int):
    db_mycard = (db.query(models.MyCard)
                 .filter(models.MyCard.id == mycard_id).first())

    if db_mycard:
        db.delete(db_mycard)
        db.commit()

    return db_mycard