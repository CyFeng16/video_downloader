import re
import subprocess
import threading
import time
import zlib
from pathlib import Path
from typing import Optional, Tuple, Union

from loguru import logger

# Constants
MIN_PORT = 10000
MAX_PORT = 60000
DEFAULT_DELAY = 600  # seconds


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
    video_url: str, download_option: str, base_download_path: Union[str, Path] = "/tmp"
) -> Tuple[Optional[str], str]:
    """
    Download the video from the given URL using yt-dlp.
    """

    if not video_url:
        return None, "Video URL cannot be empty."
    logger.info(video_url)
    base_download_path = Path(base_download_path)

    command_format_options = {
        "BestVideo": "bv*+ba/b",
        "BestAudio": "ba/b",
        "1080p": "(bv*[height=1080]+ba/bv*+ba/b)[height<=1080]",
        "720p": "(bv*[height=720]+ba/bv*+ba/b)[height<=720]",
    }

    command_format = command_format_options.get(download_option)
    if not command_format:
        return None, "Invalid download option."

    output_template = f"'{base_download_path}/%(title)s.f%(format_id)s.%(ext)s'"
    command = f"yt-dlp -f '{command_format}' -o {output_template} --force-overwrites {video_url}"

    try:
        process = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
        if process.returncode == 0:
            file_path = parse_download_path(process.stdout + process.stderr)
            if file_path:
                delayed_delete(file_path.as_posix())
                return file_path.as_posix(), "Download successful."
            else:
                return (
                    None,
                    "Download successful, but unable to determine the file name.",
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
