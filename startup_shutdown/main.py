from fastapi import FastAPI

app = FastAPI()

items = {}


@app.on_event("shutdown")
async def shutdown_event():
    with open("log.txt", mode="a") as log:
        log.write("Application shutdown")


@app.get("/items")
async def read_items():
    return [{"name": "Foo"}]
