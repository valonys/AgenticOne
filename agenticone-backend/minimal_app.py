from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Minimal FastAPI app working!"}

@app.get("/health")
def health():
    return {"status": "healthy"}
