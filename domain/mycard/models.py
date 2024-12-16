from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
import enum 

from sqlalchemy.dialects.mysql import INTEGER, ENUM

class CardType(enum.Enum):
    credit = "credit"
    check = "check"

class Card(Base):
    __tablename__ = 'card'

    card_id = Column(INTEGER(unsigned=True), primary_key=True, index=True)
    card_name = Column(String(100), index=True)
    card_image = Column(String(255))
    company = Column(String(100), index=True)
    type = Column(ENUM('credit', 'check'))  # Enum 타입 적용
    hash_key = Column(String(36), unique=True)

    benefits = relationship("Benefit", back_populates="card")
    mycards = relationship("MyCard", back_populates="card")

class Benefit(Base):
    __tablename__ = 'benefit'

    benefit_id = Column(INTEGER(unsigned=True), primary_key=True, index=True)
    card_id = Column(INTEGER(unsigned=True), ForeignKey('card.card_id'))
    category = Column(String(20), nullable=True)
    title = Column(String(255), nullable=True)
    description = Column(String(255), nullable=True)
    card_hash_key = Column(String(36))

    card = relationship("Card", back_populates="benefits")

class MyCard(Base):
    __tablename__ = 'myCard'

    myCard_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    card_id = Column(INTEGER(unsigned=True), ForeignKey('card.card_id'))

    card = relationship("Card", back_populates="mycards", lazy="joined")