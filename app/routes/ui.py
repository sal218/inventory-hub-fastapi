from datetime import timedelta
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import jwt

from app.database import get_db
from app import crud, schemas
from app.models import User, Category
from app.routes.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from app.currency_utils import get_exchange_rate


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request" : request}) # loads index.html aka home page

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request" : request}) # loads login.html page


@router.post("/login", response_class=HTMLResponse)
async def login_user(
    request: Request,
    username: str = Form(...), # extracts username from submitted form
    password: str = Form(...), # extracts password from submitted form
    db: Session = Depends(get_db)
):  
    # check user credentials from db
    user = db.query(User).filter(User.username == username).first()
    # if username or password not correct, load login.html page with error message
    if not user or not crud.pwd_context.verify(password, user.password):
        return templates.TemplateResponse("login.html", {"request" : request, "error" : "Invalid Credentials"})
    
    # create a JWT token 
    token = create_access_token(
        data={'sub': user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # create a response and set token in a cookie
    response = RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request" : request}) # loads registration page


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    role:  str = Form(...),
    db: Session = Depends(get_db)
):
    # we first check if the user exists
    exisiting_user = db.query(User).filter(User.username == username).first()
    if exisiting_user:
        return templates.TemplateResponse("register.html", {"request" : request, "error" : "User already registered"})
    
    # now we can create the user 
    user_in = schemas.UserCreate(username=username, password=password, role=role)
    try:
        crud.create_user(db, user_in)
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request" : request, "error" : f"Registration failed: {str(e)}"})
    
    # redirect to login page once user reigsters their account
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return response

#cookie based dependancy. Retrieves token from the requests cookies (instead of expecting authorization header)
def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


# route to user profile page
@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, current_user: schemas.User = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse("profile.html", {"request" : request, "current_user" : current_user})

# logout route to redirect user to login page after they logout
@router.get("/logout")
async def logout(_request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response


@router.get("/inventory/manage", response_class=HTMLResponse)
async def manage_inventory(
    request: Request,
    search: str | None = None,
    page: int = 1,
    category_id: str | None = None, 
    current_user: User = Depends(get_current_user_from_cookie), 
    db: Session = Depends(get_db)
    ):
        limit = 10
        skip = (page - 1) * limit
        cat_id = int(category_id) if category_id and category_id.strip() else None 

        items = crud.get_items(db, skip=skip, limit=limit)

        prev_page = page - 1 if page > 1 else None
        next_page = page + 1 if len(items) == limit else None

        categories = crud.get_categories(db)
        categories_data = [{"category_id": cat.category_id, "name": cat.name} for cat in categories]
        return templates.TemplateResponse("manage_inventory.html", {
            "request": request, 
            "current_user": current_user, 
            "limit" : limit,
            "prev_page" : prev_page,
            "next_page" : next_page,
            "search": search,
            "items": items,
            "categories": categories_data
        })


@router.get("/inventory/view", response_class=HTMLResponse)
async def view_inventory(
    request: Request, 
    search: str | None = None, 
    category_id: str | None = None,
    currency: str = "CAD", 
    page: int = 1, 
    current_user: User = Depends(get_current_user_from_cookie), 
    db: Session = Depends(get_db)
):
    limit = 10
    skip = (page - 1) * limit

    cat_id = int(category_id) if category_id and category_id.strip() else None # convert category_id to int if provided and is non-empty; otherwise we can set to None

    items = crud.get_items(db, skip=skip, limit=limit, search=search, category_id=category_id)

    exchange_rate = 1.0
    if currency != "CAD":
        exchange_rate = await get_exchange_rate("CAD", currency) # get exchange rate
    
    # apply the exchange rate to item prices dynamically
    for item in items:
        item.price = float(item.price) * exchange_rate

    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if len(items) == limit else None

    categories = crud.get_categories(db)

    return templates.TemplateResponse("view_inventory.html", {
        "request" : request,
        "current_user" : current_user,
        "items" : items,
        "prev_page" : prev_page,
        "next_page" : next_page,
        "page" : page,
        "search" : search,
        "selected_category" : cat_id,
        "currency" : currency,
        "exchange_rate" : exchange_rate,
        "categories" : categories   
    })

@router.post("/inventory/add", response_class=RedirectResponse)
async def add_inventory_item(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    quantity: int = Form(...),
    price: float = Form(...),
    category: str = Form(...),  
    category_id: str = Form(""),  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    
    if category_id:
        cat_id = int(category_id)
    else:
        
        existing_cat = db.query(Category).filter(Category.name == category).first()
        if existing_cat:
            cat_id = existing_cat.category_id
        else:
           
            new_cat = crud.create_category(db, schemas.CategoryCreate(name=category, description=""))
            cat_id = new_cat.category_id

    item_data = schemas.InventoryItemCreate(
        name=name,
        description=description,
        quantity=quantity,
        price=price,
        category_id=cat_id,
        created_by=current_user.user_id
    )
    crud.create_item(db, item_data)
    return RedirectResponse(url="/inventory/manage", status_code=status.HTTP_302_FOUND)


@router.post("/inventory/edit/{item_id}", response_class=RedirectResponse)
async def edit_inventory_item(
    item_id: int,
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    quantity: int = Form(...),
    price: float = Form(...),
    category: str = Form(""),  
    category_id: str = Form(...),  
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie)
):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    
    if category.strip():  
        
        existing_cat = db.query(Category).filter(Category.name == category).first()
        if existing_cat:
            cat_id = existing_cat.category_id
        else:
            
            new_cat = crud.create_category(db, schemas.CategoryCreate(name=category, description=""))
            cat_id = new_cat.category_id
    else:
        
        cat_id = int(category_id)
    
    updates = schemas.InventoryItemUpdate(
        name=name,
        description=description,
        quantity=quantity,
        price=price,
        category_id=cat_id
    )
    crud.update_item(db, item, updates)
    return RedirectResponse(url="/inventory/manage", status_code=status.HTTP_302_FOUND)


@router.get("/inventory/delete/{item_id}", response_class=RedirectResponse)
async def delete_inventory_item(
    item_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user_from_cookie)
):
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    crud.delete_item(db, item_id)
    return RedirectResponse(url="/inventory/manage", status_code=status.HTTP_302_FOUND)







