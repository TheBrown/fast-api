from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

def generate_html_response():
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


@app.get("/items", response_class=HTMLResponse)
async def read_items():
    return generate_html_response()
