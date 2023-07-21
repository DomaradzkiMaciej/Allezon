from enum import Enum
from pydantic import BaseModel
from typing import List


class Device(str, Enum):
    PC = 'PC'
    MOBILE = 'MOBILE'
    TV = 'TV'


class Action(str, Enum):
    VIEW = 'VIEW'
    BUY = 'BUY'


class Aggregate(str, Enum):
    COUNT = 'COUNT'
    SUM_PRICE = 'SUM_PRICE'


class ProductInfo(BaseModel):
    product_id: int
    brand_id: str
    category_id: str
    price: int


#  {'product_info': {'product_id': 12486, 'brand_id': 'Ebros_Gift', 'category_id': 'Trousers', 'price': 28969}, 'time': '2022-03-01T00:00:00.649Z', 'cookie': '9WkYGxkiXBfpMIjBGURC', 'country': 'CL', 'device': 'MOBILE', 'action': 'VIEW', 'origin': 'CAMPAIGN_321'}

class UserTag(BaseModel):
    time: str
    cookie: str
    country: str
    device: Device
    action: Action
    origin: str
    product_info: ProductInfo


class UserProfile(BaseModel):
    cookie: str
    buys: List[UserTag]
    views: List[UserTag]
