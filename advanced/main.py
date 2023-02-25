from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

app = FastAPI()


@app.post("/cookie-and-object")
def create_cookie(response: Response):
    content = {"message": "Come to the dark side, we have cookies"}
    response = JSONResponse(content)
    response.set_cookie(key="fakesession", value="fake-cookie-session-value")
    return response

