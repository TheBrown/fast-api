from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/typer")
async def redirect_typer():
    return RedirectResponse("https://typer.tiangolo.com")


@app.get("/saleumsack", response_class=RedirectResponse)
async def redirect_fastapi():
    return "https://saleumsack.com"
