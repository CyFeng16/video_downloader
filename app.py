import os
from pathlib import Path
from typing import Optional, Any

import gradio as gr
import requests
from gradio import DownloadButton, Textbox, Button
from loguru import logger

# Constants
LOCAL_IP: str = os.getenv("LOCAL_IP", "0.0.0.0")
LOCAL_PORT: int = int(os.getenv("LOCAL_PORT", 10652))
REMOTE_IP: str = os.getenv("REMOTE_IP", "0.0.0.0")
REMOTE_PORT: int = int(os.getenv("REMOTE_PORT", 10651))
DOWNLOAD_API_URL: str = f"http://{REMOTE_IP}:{REMOTE_PORT}/download_stream"
FILE_API_URL: str = f"http://{REMOTE_IP}:{REMOTE_PORT}/download_file"
# Ensure the download directory exists
DOWNLOAD_PATH: Path = Path.cwd() / "downloads"
DOWNLOAD_PATH.mkdir(parents=True, exist_ok=True)


def setup_gradio_interface() -> gr.Blocks:
    """
    Sets up the Gradio interface for video downloading.

    Returns:
        A Gradio Blocks interface for downloading videos.
    """

    with gr.Blocks(
        title="Video Downloader",
    ) as interface:
        gr.Markdown(
            """
            # [Video Downloader](https://github.com/CyFeng16/video_downloader)

            This app allows you to download videos from various websites. 
            You can specify the quality and format of the downloaded video or audio.
            """
        )
        with gr.Column():
            input_url = gr.Textbox(
                label="Video URL: ", placeholder="Please input video URL: "
            )
            quality_options = gr.Dropdown(
                choices=["best", "worst"],
                value="best",
                label="Quality Option: ",
            )
            content_options = gr.Dropdown(
                choices=["video", "audio"],
                value="video",
                label="Content Option: ",
            )
            output_msg = gr.Textbox(
                label="Messages: ",
                placeholder="Downloaded video will be displayed here.",
                visible=True,
            )
            cap_btn = gr.Button(value="Video Capture")
            down_btn = gr.DownloadButton(
                visible=False,
            )

        cap_btn.click(
            fn=download_stream_wrapper,
            inputs=[input_url, quality_options, content_options, cap_btn, down_btn],
            outputs=[output_msg, cap_btn, down_btn],
        ).then(
            fn=download_file_wrapper,
            inputs=[output_msg],
            outputs=[down_btn],
        )

        down_btn.click(
            fn=reset_gradio_interface,
            inputs=[],
            outputs=[input_url, output_msg, cap_btn, down_btn],
        )

    return interface


def reset_gradio_interface() -> tuple[Textbox, Textbox, Button, DownloadButton]:
    """Resets the Gradio interface to its initial state."""

    return (
        gr.Textbox(
            label="Video URL: ",
            placeholder="Please input video URL: ",
        ),
        gr.Textbox(
            label="Messages: ",
            placeholder="Downloaded video will be displayed here.",
            visible=True,
        ),
        gr.Button(value="Video Capture", visible=True),
        gr.DownloadButton(visible=False),
    )


def download_stream_wrapper(
    video_url: str,
    quality_options: str,
    format_options: str,
    cap_btn: gr.Button,
    down_btn: gr.DownloadButton,
) -> tuple[Any, Button, DownloadButton] | tuple[str, Button, DownloadButton]:
    response = requests.post(
        DOWNLOAD_API_URL,
        params={
            "url": video_url,
            "quality": quality_options,
            "content_type": format_options,
        },
    )

    if response.status_code == 200:
        logger.info("Download initiation request succeeded.")
        file_name = response.json().get("message")
        cap_btn = gr.Button(
            visible=False,
        )
        down_btn = gr.DownloadButton(
            visible=True,
            label="Video Download",
        )
        return file_name, cap_btn, down_btn
    else:
        logger.error(f"Request failed with status code: {response.status_code}")
    return (
        "Failed to download with status code: {response.status_code}",
        cap_btn,
        down_btn,
    )


def download_file_wrapper(file_name: str) -> Optional[Path]:
    response = requests.get(FILE_API_URL, params={"file_name": file_name})
    if response.status_code == 200:
        logger.info("File download request succeeded.")
        file_path = DOWNLOAD_PATH / file_name
        file_path.write_bytes(response.content)
        return file_path
    else:
        logger.error(f"File download failed with status code: {response.status_code}")
        return None


if __name__ == "__main__":
    demo = setup_gradio_interface()
    demo.queue()
    demo.launch(server_name=LOCAL_IP, server_port=LOCAL_PORT, show_api=False)
