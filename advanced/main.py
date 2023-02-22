from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()


@app.get("/items")
async def read_items():
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1> Look my! HTML!</h1>
            <p>this is so nice though </p>
        </body>
    </html>
    """

    return HTMLResponse(content=html_content, status_code=200)
