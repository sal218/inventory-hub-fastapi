from fastapi import FastAPI
from app.database import engine, Base
from fastapi.staticfiles import StaticFiles
from app.routes import items, categories, suppliers, auth, ui, oauth, api_dashboard


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Management System API")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(categories.router, prefix="/categories", tags=["Categories"])
app.include_router(suppliers.router, prefix="/suppliers", tags=["Suppliers"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(ui.router, prefix="", tags=["UI"])
app.include_router(oauth.router, tags=["OAuth"])
app.include_router(api_dashboard.router, tags=["API"])