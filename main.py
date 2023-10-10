import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8080,
        workers=4,
        log_level="debug",
        reload=True,
    )
