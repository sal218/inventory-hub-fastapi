from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.models import User


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
    # load the home page after sucessful login 
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
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
    response = RedirectResponse(url="/ui/login", status_code=status.HTTP_302_FOUND)
    return response

