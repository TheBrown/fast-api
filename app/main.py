from typing import Union, List, Any
from enum import Enum
from fastapi import FastAPI, Query, Path, Body, Cookie, Header, status, HTTPException
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from uuid import UUID
from datetime import datetime, time, timedelta

fake_items_db = [{"item_name": "Love"}, {
    "item_name": "You"}, {"item_name": "My Heart"}]

wrestler_list = {"foo": "The Foo Wrestlers"}


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


class MyItem(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None
    tags: List[str] = []


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Union[str, None] = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: Union[str, None] = None


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ...not really")
    return user_in_db


app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World", "message": "Play with fast api"}


@app.get("/wrestlers/{wrestler_id}")
async def read_wrestler(wrestler_id: str):
    if wrestler_id not in wrestler_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Wrestler not found!",
                            headers={"X-Error": "There goes my error"})
    return {"wrestler": wrestler_list[wrestler_id]}


@app.get("/items-header")
async def read_items(
        user_agent: Union[str, None] = Header(default=None),
        strange_header: Union[str, None] = Header(default=None, convert_underscores=False),
        x_token: Union[List[str], None] = Header(default=None)
):
    return {"User-agent": user_agent, "strange_header": strange_header, "X-Token values": x_token}


@app.get("/items-cookie")
async def read_items(ads_id: Union[str, None] = Cookie(default=None)):
    return {"ads_id": ads_id}


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
async def read_items(
        item_id: UUID,
        start_datetime: Union[datetime, None] = Body(default=None),
        end_datetime: Union[datetime, None] = Body(default=None),
        repeat_at: Union[time, None] = Body(default=None),
        process_after: Union[timedelta, None] = Body(default=None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_datetime
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration
    }


@app.post("/items", status_code=status.HTTP_201_CREATED)
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


@app.post("/my-items")
async def create_item(item: MyItem) -> MyItem:
    return item


@app.get("/my-items")
async def read_items() -> List[MyItem]:
    return [
        MyItem(name="Portal Gun", price=42.0),
        MyItem(name="Plumbus", price=32.0),
    ]


@app.post("/user", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved
