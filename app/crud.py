from sqlalchemy.orm import Session
from app.models import(
    InventoryItem, Category, Supplier, User, ItemSupplier
)
from app.schemas import (
    InventoryItemCreate, InventoryItemUpdate,
    SupplierCreate, SupplierUpdate,
    CategoryCreate, CategoryUpdate,
    UserCreate, UserUpdate, UserPasswordUpdate
    
)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # this is used so we can apply password hashing for more security


# Inventory Item CRUD

# create a new inventory item
def create_item(db: Session, item: InventoryItemCreate) -> InventoryItem:
    db_item = InventoryItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# retrieve an inventory item by its id
def get_item(db: Session, item_id: int) -> InventoryItem | None:
    return db.query(InventoryItem).filter(InventoryItem.item_id == item_id).first() # queries the InventoryItem table where row matches with item_id

def get_items(db: Session, skip: int = 0, limit: int = 10, search: str | None = None, category_id: int | None = None) -> list[InventoryItem]:
    query = db.query(InventoryItem)
    if search:
        query = query.filter(InventoryItem.name.ilike(f"%{search}")) # filters item where name contains the search term or even partial matches
    if category_id:
        query = query.filter(InventoryItem.category_id == category_id) # filters item by the category if it is provided 
    return query.offset(skip).limit(limit).all() # skips first defined skip value records, limits the number of results and returns a list of results


# update a specific inventory item based on provided data
def update_item(db: Session, db_item: InventoryItem, updates: InventoryItemUpdate) -> InventoryItem:
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

# delete an inventory item
def delete_item(db: Session, item_id: int) -> InventoryItem | None:
    db_item = get_item(db, item_id) # call get_item function and pass in db and item_id
    if db_item:
        db.delete(db_item)
        db.commit()
    return db_item


# Category CRUD

def create_category(db: Session, category: CategoryCreate) -> Category:

    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_category(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.category_id == category_id).first()

def get_categories(db: Session, skip: int = 0, limit: int = 10, search: str | None = None) -> list[Category]:
    query = db.query(Category)
    if search:
        query = query.filter(Category.name.ilike(f"{search}")) # enable category search
    return query.offset(skip).limit(limit).all()

def update_category(db: Session, db_category: Category, updates: CategoryUpdate) -> Category: 
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int) -> Category | None:
    db_category = get_item(db, category_id)
    if category_id:
        db.delete(category_id)
        db.commit()
    return db_category


# Supplier CRUD

def create_supplier(db: Session, supplier: SupplierCreate) -> Supplier:
    db_supplier = Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def get_supplier(db: Session, supplier_id: int) -> Supplier | None:
    return db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

def get_suppliers(db: Session, skip: int = 0, limit: int = 10, search: str | None = None) -> list[Supplier]:
    query = db.query(Supplier)
    if search:
        query = query.filter(Supplier.name.ilike(f"{search}"))
    return query.offset(skip).limit(limit).all()


def update_supplier(db: Session, db_supplier: Supplier, updates: SupplierUpdate) -> Supplier:
    update_data = updates.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_supplier,key, value)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

def delete_supplier(db: Session, supplier_id: int) -> Supplier | None:
    db_supplier = get_supplier(db, supplier_id)
    if db_supplier:
        db.delete(db_supplier)
        db.commit()
    return db_supplier

   




