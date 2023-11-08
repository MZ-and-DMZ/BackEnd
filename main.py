import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from models import mongodb
from routers import auth, aws, gcp, groups, postitions, users
from src.config import conf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(postitions.router)
app.include_router(aws.router)
app.include_router(gcp.router)
app.include_router(groups.router)


@app.on_event("startup")
async def startup_event():
    mongodb.connect(conf["db_server_url"])


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
