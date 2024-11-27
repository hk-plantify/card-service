from pydantic import BaseModel
from typing import Optional

class CardBase(BaseModel):
    name: str
    image: Optional[str] = None
    company: str
    type: str

class CardCreate(CardBase):
    pass

class CardResponse(CardBase):
    id: int

    class Config:
        orm_mode = True

class MyCardBase(BaseModel):
    card_id: int

class MyCardCreate(MyCardBase):
    pass

class MyCardResponse(MyCardBase):
    id: int
    card: Optional[CardResponse]

    class Config:
        orm_mode = True