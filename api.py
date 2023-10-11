from fastapi import FastAPI

app = FastAPI()


@app.get(path="/")
async def root():
    return {"message": "Hello, World!"}
