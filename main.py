import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from routers import routers
from src.config import settings
from src.database import mongodb

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # 모든 헤더 허용
)

for router in routers:
    app.include_router(router)


@app.on_event("startup")
async def startup_event():
    mongodb.connect(settings["db_server_url"])


@app.on_event("shutdown")
async def shutdown_event():
    mongodb.close()


@app.get(path="/")
async def root():
    return FileResponse("./public/index.html")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        log_level="debug",
        reload=True,
    )
