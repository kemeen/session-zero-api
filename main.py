from fastapi import FastAPI
from routes import spell

app = FastAPI()

app.include_router(spell.router, tags=["Spells"])

@app.get("/")
def default_route() -> dict:
    return {"Status": "OK", "message": "Welcome to the session-zero API"}
