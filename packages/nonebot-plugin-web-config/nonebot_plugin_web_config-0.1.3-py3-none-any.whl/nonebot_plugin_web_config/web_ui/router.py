import asyncio
import threading
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager

from .config import config
from .util import process_data

Root = Path(__file__).parent
templates = Jinja2Templates(directory=Root / "templates")
app = FastAPI()
app.mount("/static", StaticFiles(directory=(Root / "templates/static")), name="static")

InvalidCredentialsException = HTTPException(
    status_code=303, headers={"Location": "/login"}
)

manager = LoginManager(
    secret="some-secret-key",
    token_url="/login",
    use_cookie=True,
    custom_exception=InvalidCredentialsException,
)


@manager.user_loader()
async def get_current_user(user: str = Depends(manager)):
    if user == config.web_user:
        return user
    else:
        raise manager.not_authenticated_exception


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    if username != config.web_user or password != config.web_passwd:
        raise manager.not_authenticated_exception
    token = manager.create_access_token(data={"sub": username})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/{full_path:path}")
async def index_page(
    request: Request, full_path: str, current_user: str = Depends(get_current_user)
):
    from .util import generate_index

    menu, data = generate_index(full_path)

    return templates.TemplateResponse(
        "index.jinja2", {"request": request, "menu": menu, "data": data}
    )


@app.post("/{full_path:path}")
async def index_post(
    request: Request, full_path: str, current_user: str = Depends(get_current_user)
):
    await process_data(full_path, request)


async def run_server():
    web_ui_thread = threading.Thread(
        target=lambda: uvicorn.run(app, host=config.web_host, port=config.web_port)
    )
    web_ui_thread.daemon = True
    web_ui_thread.start()


asyncio.run(run_server())
