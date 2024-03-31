from pathlib import Path
from typing import Union, Dict, Literal, Optional

import yt_dlp
from loguru import logger

# Constants
QUALITIES = {
    "video": {
        "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "worst": "worstvideo+worstaudio/worst",
    },
    "audio": {"best": "bestaudio/best", "worst": "worstaudio/worst"},
}
EXTENSIONS = {"video": "mp4", "audio": "mp3"}
DEFAULT_DOWNLOAD_DIR = Path("downloads")
BEST_QUALITY_AUDIO = "320"
WORST_QUALITY_AUDIO = "128"

ContentType = Literal["video", "audio"]
QualityType = Literal["best", "worst"]


def ensure_directory_exists(directory: Path) -> None:
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")


def configure_download_options(
    quality: QualityType, content_type: ContentType, download_dir: Path
) -> Dict:
    format_selection = QUALITIES[content_type][quality]
    out_template = (download_dir / "%(title)s.%(ext)s").as_posix()

    options = {
        "format": format_selection,
        "outtmpl": out_template,
        "overwrites": True,
        "progress_hooks": [],
    }

    if content_type == "audio":
        options["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": EXTENSIONS[content_type],
                "preferredquality": (
                    BEST_QUALITY_AUDIO if quality == "best" else WORST_QUALITY_AUDIO
                ),
            }
        ]

    return options


def download_content(
    url: str,
    quality: QualityType,
    content_type: ContentType,
    download_dir: Union[str, Path],
) -> Optional[str]:
    if quality not in QUALITIES[content_type]:
        logger.error("Invalid quality provided.")
        return "Invalid quality"
    if content_type not in QUALITIES:
        logger.error("Invalid content type provided.")
        return "Invalid content type"

    download_dir = Path(download_dir).absolute()
    ensure_directory_exists(download_dir)

    options = configure_download_options(quality, content_type, download_dir)

    def progress_hook(d):
        nonlocal file_name
        if d["status"] == "finished":
            logger.info(f"Download finished: {d['filename']}")
            file_name = f'{d["info_dict"]["title"]}.{EXTENSIONS[content_type]}'

    options["progress_hooks"].append(progress_hook)

    file_name = "None"
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])
            logger.info(f"Download finished: {download_dir / file_name}")
            return file_name
    except Exception as e:
        logger.error(f"Failed to download: {e}")
