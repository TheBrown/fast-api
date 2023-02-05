from typing import Union
from enum import Enum

from fastapi import FastAPI

class ModelName(str, Enum):
    bobby = "bobby"
    alexis = "alexis"
    novak = "novak"


app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World", "message": "Play with fast api"}

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    return {"item_id": item_id}

@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id":  user_id}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.bobby:
        return {"model_name": model_name, "message": "Hi Bobby model!"}
    if model_name is ModelName.novak:
        return {"model_name": model_name, "message": "Hi Novak model!"}
    return {"model_name": model_name, "message": "there are some problems with this model"}