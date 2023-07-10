from enum import Enum
from pydantic import BaseModel
from typing import List
from datetime import datetime

class Device(Enum):
    PC = 'PC'
    MOBILE = 'MOBILE'
    TV = 'TV'

class Action(Enum):
    VIEW = 'VIEW'
    BUY = 'BUY'

class Aggregate(Enum):
    COUNT = 'COUNT'
    SUM_PRICE = 'SUM_PRICE'

class ProductInfo(BaseModel):
    product_id: str
    brand_id: str
    category_id: str
    price: int

class UserTag(BaseModel):
    time: datetime
    cookie: str
    country: str
    device: Device
    action: Action
    origin: str
    product_info: ProductInfo

class UserProfile(BaseModel):
    cookie: str
    view: List[UserTag]
    buys: List[UserTag]