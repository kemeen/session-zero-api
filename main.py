from fastapi import FastAPI

app = FastAPI()

app.get("/")
def default_route() -> dict:
    return {"Status": "OK", "message": "Welcome to the session-zero API"}
