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

    with gr.Blocks(
        title="Video Downloader",
    ) as interface:
        with gr.Row():
            gr.Markdown(
                """
                # [Video Downloader](https://github.com/CyFeng16/video_downloader)
                
                This app allows you to download videos from YuoTebu/BliiBlii/Purnhob and other websites. 
                You can specify the quality and format of the downloaded video.
                """
            )
        with gr.Row():
            input_url = gr.Textbox(label="Input Video URL: ")
            quality_options = gr.Dropdown(
                choices=["BestVideo", "BestAudio", "1080p", "720p"],
                value="BestVideo",
                label="Quality Option: ",
            )
            format_options = gr.Dropdown(
                choices=["auto", "mp4", "webm"],
                value="auto",
                label="Format Option: ",
            )
        with gr.Row():
            output_file = gr.Video(
                label="Video Downloaded: ",
                height=480,
                width=640,
                autoplay=True,
                show_download_button=True,
            )
        with gr.Row():
            output_msg = gr.Textbox(label="Messages: ")

        btn = gr.Button(value="Download!")
        btn.click(
            fn=download_video_wrapper,
            inputs=[input_url, quality_options, format_options],
            outputs=[output_file, output_msg],
        )

    return interface


def download_video_wrapper(
    video_url: str,
    quality_options: str,
    format_options: str,
) -> Tuple[Path, str]:
    """
    Wrapper function for `download_video` to adapt its return values for Gradio outputs.

    Args:
        video_url (str): The URL of the video to download.
        quality_options (str): The download quality option.
        format_options (str): The download format option.

    Returns:
        Tuple[Path, str]: A tuple containing the path to the downloaded video and a message.
    """

    download_option = (
        quality_options,
        format_options,
        True if "audio" in quality_options.lower() else False,
    )
    file_path, message = download_video(video_url, *download_option)
    # Convert file path to a format suitable for Gradio output, if not None
    return Path(file_path) if file_path else None, message


if __name__ == "__main__":
    demo = setup_gradio_interface()
    demo.queue()
    demo.launch(
        server_name=LOCAL_CLIENT_IP,
        server_port=DEFAULT_PORT,
    )
