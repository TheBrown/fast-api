from fastapi import FastAPI
from fastapi.responses import FileResponse

some_file_path = "large-video-file.txt"
app = FastAPI()


@app.get("/")
async def main():
    return FileResponse(some_file_path)
