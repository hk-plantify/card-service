from pydantic import BaseModel
from typing import List, Optional

class CardBase(BaseModel):
    name: str
    image: Optional[str] = None
    company: str
    type: str

class CardCreate(CardBase):
    pass

class BenefitResponse(BaseModel):
    title: str
    
    class Config:
        orm_mode = True
        from_attributes = True

class CardResponse(CardBase):
    card_id: int
    benefits: List[str]

    class Config:
        orm_mode = True

class MyCardBase(BaseModel):
    card_id: int

class MyCardCreate(MyCardBase):
    user_id: int

class MyCardResponse(MyCardBase):
    id: int
    card: Optional[CardResponse]

    class Config:
        orm_mode = True
        from_attributes = True