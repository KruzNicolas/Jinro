
from fastapi import FastAPI

from .routers import shortener

app = FastAPI()
app.include_router(shortener.router)
