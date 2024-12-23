from fastapi import FastAPI
from database import engine, Base
from routers.users import router
from routers.protected import router_prot
from routers.resumes import router_res
from routers.vacancies import router_vac
app = FastAPI(title="HR Monitor", debug=True)


Base.metadata.create_all(bind=engine)

app.include_router(router, prefix="/api/v1", tags=['Users'])
app.include_router(router_prot, prefix="/api/v2")
app.include_router(router_vac, prefix="/api/v3")
app.include_router(router_res, prefix="/api/v4")

@app.get("/")
def read_root():
    return {"message": "HR Monitor is running"}