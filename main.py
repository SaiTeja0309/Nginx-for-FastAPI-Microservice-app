from fastapi import FastAPI, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models import User
import hashlib

Base.metadata.create_all(bind=engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Simple in-memory session (not production safe)
logged_in_users = {}

def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

@app.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
def signup(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Username already exists!"})
    user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        password=hash_password(password)
    )
    db.add(user)
    db.commit()
    return RedirectResponse("/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username, User.password == hash_password(password)).first()
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    logged_in_users[username] = True
    return RedirectResponse(f"/account?username={username}", status_code=303)

@app.get("/account", response_class=HTMLResponse)
def account(request: Request, username: str):
    if username not in logged_in_users:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse("account.html", {"request": request, "username": username})
