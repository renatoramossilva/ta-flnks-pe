"""Main entry point for the FastAPI application."""

from fastapi import FastAPI

from app.api.routes import news

app = FastAPI()

app.include_router(news.router)
