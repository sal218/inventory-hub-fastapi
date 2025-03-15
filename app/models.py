from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone


class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(datetime, default=lambda: datetime.now(timezone.utc)) # lambda ensures dynamic time sets

    # One category can have many inventory items. We can use this setup to access all inventory items that belong to a certain category
    items = relationship("InventoryItem", back_populates="category")

class InventoryItem(Base):
    __tablename__ = "inventory_items"
    
    item_id = Column(Integer, primary_key=True, Index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Numeric)
    category_id = Column(Integer, ForeignKey())

    category = relationship("categories", back_populates="items")


class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_details = Column()
