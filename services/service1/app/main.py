from fastapi import FastAPI

app = FastAPI(
    title="Service 1",
    root_path="/service1"
)

@app.get("/")
def root():
    return {"service": "service1", "message": "Hello from Service 1"}
