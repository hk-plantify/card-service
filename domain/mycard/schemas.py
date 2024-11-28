from pydantic import BaseModel
from typing import List, Optional

class CardBase(BaseModel):
    name: str
    image_url: Optional[str] = None
    company_name: str
    card_type: str

class CardCreate(CardBase):
    pass

class BenefitResponse(BaseModel):
    benefit_description: str
    
    class Config:
        orm_mode = True
        from_attributes = True

class CardResponse(CardBase):
    card_id: int
    benefits: List[BenefitResponse]

    class Config:
        orm_mode = True
        from_attributes = True

class MyCardBase(BaseModel):
    card_id: int

class MyCardCreate(MyCardBase):
    pass

class MyCardResponse(MyCardBase):
    id: int
    card: Optional[CardResponse]

    class Config:
        orm_mode = True
        from_attributes = True