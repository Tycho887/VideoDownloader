from scripts import download_video
import argparse

if __name__ == "__main__":
    str_in = input("Enter the video URL to download and format: ")
    try:
        url, format = str_in.split(" ")
    except ValueError:
        url = str_in
        format = 'mp4'
    download_video(url, format)


