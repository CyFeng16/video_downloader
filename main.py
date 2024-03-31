import asyncio
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from func import download_content  # Assume this module is optimized as well.

app = FastAPI()

# Constants
ALLOWED_ORIGINS = ["*"]
ALLOWED_METHODS = ["GET", "POST"]
ALLOWED_HEADERS = ["X-Custom-Header"]
DOWNLOAD_DIRECTORY_PATH = Path("/workspace/downloads")
STATIC_URL = "/static"

# Ensure the download directory exists
DOWNLOAD_DIRECTORY_PATH.mkdir(parents=True, exist_ok=True)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

app.mount(STATIC_URL, StaticFiles(directory=DOWNLOAD_DIRECTORY_PATH), name="static")


async def async_download_video(
    url: str, quality: str, content_type: str
) -> Optional[str]:
    """Asynchronous wrapper for downloading a video."""
    loop = asyncio.get_event_loop()
    try:
        downloaded_file_path: Optional[str] = await loop.run_in_executor(
            None, download_content, url, quality, content_type, DOWNLOAD_DIRECTORY_PATH
        )
        return downloaded_file_path
    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error {e}")


@app.post("/download_stream/", response_model=Dict[str, str])
async def download_stream(
    url: str = Query(..., title="URL of the video to download"),
    quality: str = Query(default="best", title="Quality of the video"),
    content_type: str = Query(default="video", title="Content type (video or audio)"),
) -> Dict[str, str]:
    """Endpoint to download a video or audio from a URL."""
    try:
        downloaded_file_path = await async_download_video(url, quality, content_type)
        return {"status": "success", "message": str(downloaded_file_path)}
    except HTTPException as http_ex:
        # This exception is raised from async_download_video, so it's caught here to return a custom response.
        return {"status": "error", "message": http_ex.detail}


@app.get("/download_file/", response_class=FileResponse)
async def download_file(
    file_name: str = Query(..., title="Name of the file to download"),
) -> FileResponse:
    """Endpoint to retrieve a downloaded file."""
    file_path = DOWNLOAD_DIRECTORY_PATH / file_name
    if not file_path.exists():
        logger.warning(f"File not found: {file_name}")
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=file_path, filename=file_name)
