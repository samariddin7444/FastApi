from pydantic import BaseModel
from typing import List, Optional


class SignUp(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password: str
    is_active: bool
    is_staff: bool

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "username": "samariddin",
                "email": "samariddimn7444@gmai.com",
                "password": "samariddin7444",
                "is_active": True,
                "is_staff": False,
            }
        }

class Login(BaseModel):
    username_or_email: str
    password: str

class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int = Field(..., gt=0)
    order_statuses: Optional[str] = "PENDING"
    user_id: Optional[int]
    product_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "quantity": 2,
                "order_statuses": "PENDING",
                "product_id": 1
            }
        }



class ProductModel(BaseModel):
    id: Optional[int]
    name: str
    price: int

    class Config:
        orm_model = True
        schema_extra = {
            "example": {
                "name": "osh",
                "price": 3000
            }
        }