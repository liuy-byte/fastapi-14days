from fastapi import FastAPI

app = FastAPI(title="FastAPI 14 Days")


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/about")
def about():
    return {"name": "fastapi-14days", "version": "0.1.0", "description": "FastAPI 14 天系统学习"}


@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}
