from datetime import timedelta
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import jwt

from app.database import get_db
from app import crud, schemas
from app.models import User
from app.routes.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM


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









