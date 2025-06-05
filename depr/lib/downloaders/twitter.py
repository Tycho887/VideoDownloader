import os
import requests
import bs4
from tqdm import tqdm
import time
from lib.utils.constants import DOWNLOAD_FOLDER as download_folder

"""
This code was gotten from: https://github.com/z1nc0r3/twitter-video-downloader
"""


def download_video(url, file_name) -> None:
    """Download a video from a URL into a filename.

    Args:
        url (str): The video URL to download
        file_name (str): The file name or path to save the video to.
    """

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)

    download_path = f"{download_folder}/{file_name}"

    with open(download_path, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)

    progress_bar.close()
    print("Video downloaded successfully!")


def download_twitter_video(url):
    """Extract the highest quality video url to download into a file

    Args:
        url (str): The twitter post URL to download from
    """

    assert os.path.exists(download_folder), "The video destination does not exist!"

    api_url = f"https://twitsave.com/info?url={url}"

    response = requests.get(api_url)
    data = bs4.BeautifulSoup(response.text, "html.parser")
    download_button = data.find_all("div", class_="origin-top-right")[0]
    quality_buttons = download_button.find_all("a")
    highest_quality_url = quality_buttons[0].get("href") # Highest quality video url

    #file name should be media + timestamp

    file_name = "twitter_media" + str(int(time.time())) + ".mp4" # Video file name
    
    download_video(highest_quality_url, file_name)

    return f"{download_folder}/{file_name}"
