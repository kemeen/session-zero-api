from fastapi import FastAPI
from routes import spell, dnd_class, race

app = FastAPI()

app.include_router(spell.router, tags=["Spells"])
app.include_router(dnd_class.router, tags=["Classes"])
app.include_router(race.router, tags=["Races"])

@app.get("/")
def default_route() -> dict:
    return {"Status": "OK", "message": "Welcome to the session-zero API"}
