import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import chat, restaurants
from services.llm import MODEL_NAME

load_dotenv(override=True)

app = FastAPI(
    title="AI Food Recommendation API",
    description="AI gợi ý món ăn & quán ăn theo ngữ cảnh người dùng — powered by Gemma 4 31B",
    version="1.0.0",
)

# CORS
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
allowed_origins = [o.strip() for o in allowed_origins_raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router, prefix="/api")
app.include_router(restaurants.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "model": MODEL_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
