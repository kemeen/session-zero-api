from fastapi import FastAPI
from routes.routes import router

characters = []

app = FastAPI()
app.include_router(router=router)
