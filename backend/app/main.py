from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"msg": "Writer & Screenwriter Assistant Backend Running"}
