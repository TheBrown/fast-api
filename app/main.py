from typing import Union, List, Any
from enum import Enum
from fastapi import FastAPI, Query, Path, Body, Cookie, Header, status, HTTPException, Depends, Request
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from uuid import UUID
from datetime import datetime, time, timedelta

SECRET_KEY = "425e89cffd75d8ab0c68678288cda4a5e20091b94b3375fb190289b9e0c2a31a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_db = {}

fake_items_db = [{"item_name": "Love"}, {
    "item_name": "You"}, {"item_name": "My Heart"}]

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

wrestler_list = {"foo": "The Foo Wrestlers"}

# app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])

description = """
ChimichangeApp API Helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
 """

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/"
        }
    }
]

app = FastAPI(openapi_tags=tags_metadata)

origins = [
    "http://localhost.tianglo.com",
    "https://localhost.tianglo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def add_process_time_head(request: Request, call_next):
    start_time = datetime.now()
    response = await call_next(request)
    process_time = datetime.now() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


def fake_hash_password(password: str):
    return "fakehashed" + password


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


class ItemJsonCompatible(BaseModel):
    title: str
    timestamp: datetime
    description: Union[str, None] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Union[str, None] = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expire_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def fake_decode_token(token):
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate Credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        return credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ...not really")
    return user_in_db


async def verify_token(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header()):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/")
async def read_root():
    return {"Hello": "World", "message": "Play with fast api"}


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World", "message": "Play with fast api"}


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expire_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "Bearer"}


@app.get("/protected/items", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]


@app.get("/protected/products")
async def read_products(token: str = Depends(oauth2_scheme)):
    return {"token": token}


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
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    return current_user


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


@app.put("/items-json-compatible/{id}")
def update_item(id: str, item: ItemJsonCompatible):
    json_compatible_item_data = jsonable_encoder(item)
    fake_db[id] = json_compatible_item_data
    return {"time_stamp": item.timestamp, "message": "Good to go!"}


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
