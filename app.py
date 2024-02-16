from pathlib import Path
from typing import Tuple

import gradio as gr

from func import string_to_port_crc32, download_video

# Constants
LOCAL_CLIENT_IP: str = "0.0.0.0"
APP_NAME: str = "video_downloader"
DEFAULT_PORT: int = string_to_port_crc32(APP_NAME)  # 10651


def setup_gradio_interface() -> gr.Blocks:
    """
    Sets up the Gradio interface for video downloading.

    Returns:
        A Gradio Blocks interface for downloading videos.
    """

    with gr.Blocks() as interface:
        with gr.Row():
            input_url = gr.Textbox(label="Input Video URL: ")
            input_options = gr.Dropdown(
                choices=["BestVideo", "BestAudio", "1080p", "720p"],
                value="BestVideo",
                label="Download Option: ",
            )
        with gr.Row():
            output_file = gr.PlayableVideo(
                label="Video Downloaded: ",
                autoplay=True,
            )
            output_msg = gr.Textbox(label="Messages: ")

        btn = gr.Button(value="Download!")
        btn.click(
            fn=download_video_wrapper,
            inputs=[input_url, input_options],
            outputs=[output_file, output_msg],
        )

    return interface


def download_video_wrapper(video_url: str, download_option: str) -> Tuple[Path, str]:
    """
    Wrapper function for `download_video` to adapt its return values for Gradio outputs.

    Args:
        video_url (str): The URL of the video to download.
        download_option (str): The download quality option.

    Returns:
        Tuple[Path, str]: A tuple containing the path to the downloaded video and a message.
    """

    file_path, message = download_video(video_url, download_option)
    # Convert file path to a format suitable for Gradio output, if not None
    return Path(file_path) if file_path else None, message


if __name__ == "__main__":
    demo = setup_gradio_interface()
    demo.launch(
        server_name=LOCAL_CLIENT_IP,
        server_port=DEFAULT_PORT,
    )
