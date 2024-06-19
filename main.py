from scripts import download_video

if __name__ == "__main__":
    url = input("Enter the video URL to download: ")
    file = download_video(url)
    print(f"Downloaded video saved as {file}")
