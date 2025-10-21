# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

#routes
from auth.routes import router as auth_router
from chess_api.routes import router as chess_router

origins = [
    "http://localhost:5173",
    "https://localhost:5173",
]

#load enviornment variables
load_dotenv()

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chess_router)

@app.get("/")
def home():
    return {"message": "Welcome to Chess Backend!"}
