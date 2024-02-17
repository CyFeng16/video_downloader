import re
import threading
import time
import zlib
from pathlib import Path
from subprocess import run, PIPE
from typing import Tuple, Optional, Union

from loguru import logger

# Constants
MIN_PORT = 10000
MAX_PORT = 60000
DEFAULT_DELAY = 600  # seconds
BEST_VIDEO = "BestVideo"
FORMAT_AUTO = "auto"
BASE_DOWNLOAD_PATH = Path("/tmp")


def string_to_port_crc32(s: str) -> int:
    """
    Convert the given string to a port number using CRC32.
    """
    crc32_value = zlib.crc32(s.encode()) & 0xFFFFFFFF
    port = MIN_PORT + crc32_value % (MAX_PORT - MIN_PORT)
    return port


def delayed_delete(file_path: Union[str, Path], delay: int = DEFAULT_DELAY) -> None:
    """
    Delayed deletion of the specified file.
    :param file_path: Path to the file to be deleted.
    :param delay: Delay time in seconds. Default is one hour.
    """

    def task():
        time.sleep(delay)
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"{file_path} has been deleted after {delay} seconds.")

    threading.Thread(target=task).start()


def download_video(
    video_url: str,
    quality_option: str = BEST_VIDEO,
    format_option: str = FORMAT_AUTO,
    audio_only: bool = False,
    base_download_path: Union[str, Path] = BASE_DOWNLOAD_PATH,
) -> Tuple[Optional[str], str]:
    """
    Download the video from the given URL using yt-dlp.
    """

    if not video_url:
        return None, "Video URL cannot be empty."
    logger.info(video_url)
    base_download_path = (
        Path(base_download_path)
        if not isinstance(base_download_path, Path)
        else base_download_path
    )

    quality_format, format_filter = get_quality_and_format_filters(
        quality_option, format_option, audio_only
    )

    output_template = base_download_path / "%(title)s.f%(format_id)s.%(ext)s"
    command = f"yt-dlp -f '{quality_format}{format_filter}' -o '{output_template}' --force-overwrites {video_url}"

    return execute_download_command(command)


def get_quality_and_format_filters(
    quality_option: str, format_option: str, audio_only: bool
) -> Tuple[str, str]:
    """
    Get the quality and format filters based on the given options.
    """

    if audio_only:
        return "bestaudio", ""
    else:
        quality_formats = {
            "Best": "b/bv*+ba",
            "1080p": "(b/bv*[height=1080]+ba/bv*+ba)[height<=1080]",
            "720p": "(b/bv*[height=720]+ba/bv*+ba)best[height<=720]",
        }
        format_filters = {
            "mp4": "[ext=mp4]",
            "webm": "[ext=webm]",
            "auto": "",
        }
        return (
            quality_formats.get(quality_option, "b/bv*+ba"),
            format_filters.get(format_option, ""),
        )


def execute_download_command(command: str) -> Tuple[Optional[str], str]:
    """
    Execute the download command and return the download path if successful.
    """

    try:
        process = run(
            command, shell=True, stdout=PIPE, stderr=PIPE, universal_newlines=True
        )
        if process.returncode == 0:
            return (
                parse_download_path(process.stdout + process.stderr),
                "Download successful.",
            )
        else:
            return None, f"Error downloading video: {process.stderr}"
    except Exception as e:
        logger.error(f"Exception occurred: {e}")
        return None, "Error executing download command."


def parse_download_path(output: str) -> Optional[Path]:
    """
    Parse the download path from the given output.
    """

    merger_match = re.search(r"\[Merger\] Merging formats into \"([^\"]+)\"", output)
    if merger_match:
        return Path(merger_match.group(1))

    download_matches = re.findall(r"\[download\] Destination: (.+)", output)
    if download_matches:
        return Path(download_matches[-1])

    return None
