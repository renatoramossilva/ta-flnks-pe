from fastapi import FastAPI
from api.routes import news

app = FastAPI()

app.include_router(news.router)
