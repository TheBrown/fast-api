from fastapi import FastAPI, Response

app = FastAPI()


@app.get("/legacy/")
def get_legacy_data():
    data = """
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
    return Response(content=data, media_type="application/xml")
