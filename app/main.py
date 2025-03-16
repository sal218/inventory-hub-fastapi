from fastapi import FastAPI
from app.database import engine, Base
from app.routes import items, categories, suppliers, auth


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Management System API")

app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])