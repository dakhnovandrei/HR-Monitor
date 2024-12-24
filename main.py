from fastapi import FastAPI
from database import engine, Base
from routers.users import router
from routers.protected import router_prot
from routers.resumes import router_res
from routers.vacancies import router_vac
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

app = FastAPI(title="HR Monitor", debug=False)

Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(router, prefix="/api/v1", tags=['Users'])
app.include_router(router_prot, prefix="/api/v2")
app.include_router(router_vac, prefix="/api/v3")
app.include_router(router_res, prefix="/api/v4")


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("static/templates/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)



