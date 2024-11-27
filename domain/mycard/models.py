from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
import enum

class CardType(enum.Enum):
    credit = "credit"
    check = "check"

class Card(Base):
    __tablename__ = 'card'

    card_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    image = Column(String(255))
    company = Column(String(255), index=True)
    type = Column(Enum(CardType))

    mycards = relationship("MyCard", back_populates="card")

class MyCard(Base):
    __tablename__ = 'myCard'

    myCard_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    card_id = Column(Integer, ForeignKey('card.card_id'))

    card = relationship("Card", back_populates="mycards")