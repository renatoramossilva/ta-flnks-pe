"""Main entry point for the FastAPI application."""

from api.routes import news
from fastapi import FastAPI

app = FastAPI()

app.include_router(news.router)
