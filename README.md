# Video Downloader

## Introduction

Video Downloader is a powerful tool designed to simplify the process of downloading videos from a variety of sources. This project leverages the functionality of [yt-dlp](https://github.com/yt-dlp/yt-dlp), a command-line program to download videos from YouTube and other video hosting sites, and provides a user-friendly interface through [Gradio](https://github.com/gradio-app/gradio), allowing for an accessible and efficient video downloading experience. Whether you're looking to download videos for offline viewing, archiving, or content creation, Video Downloader offers a versatile solution to meet your needs, thereby increasing its discoverability for those in search of a reliable video downloading utility.

## Getting Started

### Prerequisites

- Docker (recommended for simplicity)
- Git (for cloning the repository)
- Conda (for managing environments if not using Docker)

### Installation and Running the Project

#### Method 1: Using Docker (Recommended)

1. **Pull the Docker Image**

   ```bash
   docker pull cyfeng16/video_downloader:latest
   ```

2. **Run the Docker Container**

   ```bash
   docker run -p 10651:10651 cyfeng16/video_downloader:latest
   ```

   Access the application at [http://localhost:10651/](http://localhost:10651/).

#### Method 2: Cloning the Repository and Running Locally

1. **Clone the Repository**

   ```bash
   git clone https://github.com/CyFeng16/video_downloader.git
   cd video_downloader
   ```

2. **Setup the Conda Environment**

   ```bash
   conda create --name video_downloader --file requirements.txt
   conda activate video_downloader
   ```

3. **Run the Project**

   ```bash
   python app.py
   ```

   Visit [http://localhost:10651/](http://localhost:10651/) to access the project.

## Usage

This project is designed for users looking for a simple, yet effective way to download videos from various platforms. After accessing the web interface, simply paste the video URL you wish to download, select your preferred quality, and the application will handle the rest.

## Contributing

We welcome contributions to make Video Downloader even better. Whether it's feature suggestions, bug reports, or code contributions, please feel free to get involved.

## License

This project is unlicensed under the Unlicense license, allowing for unrestricted use, modification, and sharing of the software.

## Contact

- GitHub: [CyFeng16](https://github.com/CyFeng16)
- Project Link: [https://github.com/CyFeng16/video_downloader](https://github.com/CyFeng16/video_downloader)
