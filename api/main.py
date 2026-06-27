from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router
import uvicorn
import os

app = FastAPI(
    title="Traffic Violation Detection API",
    description="Real-time traffic violation detection system for Bangalore",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("output/screenshots", exist_ok=True)
app.mount("/screenshots", StaticFiles(directory="output/screenshots"), name="screenshots")

app.include_router(router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "message": "Traffic Violation Detection System",
        "version": "1.0.0",
        "city": "Bangalore",
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)