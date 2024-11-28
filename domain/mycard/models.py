from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
import enum 

from sqlalchemy.dialects.mysql import INTEGER, ENUM

class CardType(enum.Enum):
    credit = "credit"
    check = "check"

class Card(Base):
    __tablename__ = 'card_info'

    card_id = Column(INTEGER(unsigned=True), primary_key=True, index=True)
    name = Column(String(100), index=True)
    image_url = Column(String(255))
    company_name = Column(String(100), index=True)
    card_type = Column(ENUM('credit', 'check'))  # Enum 타입 적용
    hash_key = Column(String(36), unique=True)

    benefits = relationship("Benefit", back_populates="card")
    mycards = relationship("MyCard", back_populates="card")

class Benefit(Base):
    __tablename__ = 'card_benefits'

    benefit_id = Column(INTEGER(unsigned=True), primary_key=True, index=True)
    card_id = Column(INTEGER(unsigned=True), ForeignKey('card_info.card_id'))
    benefit_category = Column(String(20), nullable=True)
    benefit_description = Column(String(255), nullable=True)
    additional_info = Column(String(255), nullable=True)
    card_hash_key = Column(String(36))

    card = relationship("Card", back_populates="benefits")

class MyCard(Base):
    __tablename__ = 'myCard'

    myCard_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    card_id = Column(INTEGER(unsigned=True), ForeignKey('card_info.card_id'))

    card = relationship("Card", back_populates="mycards")