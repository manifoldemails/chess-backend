# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to Chess.com Clone Backend!"}

@app.get("/ping")
def ping():
    return {"status": "ok"}
