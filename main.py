# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_db_and_tables
from auth.routes import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ✅ This runs when the app starts up
    print("🚀 Starting up and creating database...")
    create_db_and_tables()
    yield
    # ✅ This runs when the app shuts down
    print("🛑 Shutting down...")

app = FastAPI(
    title="Chess.com  Backend",
    lifespan=lifespan
)

app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "Welcome to Chess Backend!"}
