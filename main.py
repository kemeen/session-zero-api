from fastapi import FastAPI
from routes import spells

app = FastAPI()
app.include_router(router=spells.router)

app.get("/")
def default_route() -> dict:
    return {"Status": "OK", "message": "Welcome to the session-zero API"}
