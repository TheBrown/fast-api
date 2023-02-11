from typing import Union, List
from enum import Enum
from fastapi import FastAPI, Query, Path, Body
from pydantic import BaseModel, Field, HttpUrl

fake_items_db = [{"item_name": "Love"}, {
    "item_name": "You"}, {"item_name": "My Heart"}]


class Config:
    schema_extra = {
        "example": {
            "name": "Bobby",
            "description": "A very nice person",
            "price": 1000000,
            "tax": 55000
        }
    }


class ModelName(str, Enum):
    bobby = "bobby"
    alexis = "alexis"
    novak = "novak"


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str = Field(example="Foo")
    description: Union[str, None] = Field(
        default=None, title="The description for the item.", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: Union[float, None] = None
    tags: List[str] = set()
    images: Union[List[Image], None] = Field(default=None, example=3.4)


class User(BaseModel):
    username: str
    full_name: Union[str, None] = None


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
    return {"user_id": user_id}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.bobby:
        return {"model_name": model_name, "message": "Hi Bobby model!"}
    if model_name is ModelName.novak:
        return {"model_name": model_name, "message": "Hi Novak model!"}
    return {"model_name": model_name, "message": "there are some problems with this model"}


@app.get("/items")
async def get_items(skip: int = 0, limit: int = 10):
    return fake_items_db[skip: skip + limit]


@app.get("/items/{item_id}")
async def read_items(
        item_id: int = Path("The ID of the item to get"),
        q: Union[str, None] = Query(default=None, alias="item-query")
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


@app.put("/items/{item_id}")
async def update_item(
        *,
        item_id: int,
        item: Item = Body(examples={
            "normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly.",
                "value": {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                "value": {
                    "name": "Bar",
                    "price": "35.4",
                },
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "value": {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            },
        }),
        user: User
):
    results = {"item_id": item_id, "user": user}
    if item:
        results.update({"item": item})
    return results


@app.post("/items")
async def create_item(item: Item):
    items_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        items_dict.update({"price_with_tax": price_with_tax})
    return items_dict


@app.get("/products")
async def read_products(q: Union[str, None] = Query(
    default=None,
    alias="product-query",
    title="Query String",
    description="Query String for the items to search in the database thae have a good match",
    min_length=3,
    max_length=50,
    regex="^fixedquery$",
),
):
    results = {"products": [{"product_id": "I"}, {
        "product_id": "Love"}, {"product_id": "You"}]}
    if q:
        results.update({"q": q})
    return results
