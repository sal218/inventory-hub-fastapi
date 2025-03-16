from pydantic import BaseModel, condecimal
from datetime import datetime
from decimal import Decimal
from typing import List, Annotated

# Category

class CategoryBase(BaseModel):
    name: str
    description: str | None = None

# # keeping this separate will allow for future modifications should I decide to add more. For now it extends from CategoryBase
class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    category_id: int
    created_at: datetime

    # used so that SQLAlchemy models can be converted to Pydantic objects easily
    class Config:
        orm_mode = True
    

# Inventory Item

class InventoryItemBase(BaseModel):
    name: str
    description: str | None = None
    quantity: int
    price: Annotated[Decimal, condecimal(max_digits=10, decimal_places=2)]


class InventoryItemCreate(InventoryItemBase):
    category_id: int
    created_by: int 

class InventoryItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    quantity: int | None = None
    price: Annotated[Decimal, condecimal(max_digits=10, decimal_places=2)]  | None = None
    category_id: int | None = None


class InventoryItem(InventoryItemBase):
    item_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    category: Category

    class config:
        orm_mode = True


# Supplier

class SupplierBase(BaseModel):
    name: str
    contact_details: str | None = None

# keeping this separate will allow for future modifications should I decide to add more. For now it extends from SupplierBase
class SupplierCreate(SupplierBase):
    pass

class Supplier(SupplierBase):
    supplier_id: int
    created_at: datetime

    class config:
        orm_mode = True


# User

class UserBase(BaseModel):
    username: str
    role: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    user_id: int
    created_at: datetime

    class config:
        ord_mode = True



