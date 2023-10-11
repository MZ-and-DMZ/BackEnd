from fastapi import FastAPI

app = FastAPI()


@app.get(path="/")
def root():
    return {"message": "Hello, World!"}
