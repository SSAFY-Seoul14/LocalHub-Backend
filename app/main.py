from fastapi import FastAPI

app = FastAPI(
    title="LocalHub Backend",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "LocalHub Backend API"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }