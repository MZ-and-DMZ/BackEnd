from fastapi import FastAPI

app = FastAPI()


@app.get(path="/")
def root():
    return "hello world!!"
