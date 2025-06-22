"""Main entry point for the FastAPI application."""

from fastapi import FastAPI

from app.api.routes import endpoints

app = FastAPI()

app.include_router(endpoints.router)
