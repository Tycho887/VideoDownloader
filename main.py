from scripts import download_video
from scripts._youtube import vidformats, audformats

if __name__ == "__main__":
    url = input("Enter the video URL to download: ")
    format = input(f"Choose format video/audio (supported formats: {vidformats} and {audformats}): ")
    if format in vidformats:
        print('Downloading video...')
        file = download_video(url, format)
        print(f"Downloaded video saved as {file}")
    elif format in audformats:
        print('Downloading audio...')
        file = download_video(url, format)
        print(f"Downloaded video saved as {file}")
    else:
        print("The format you entered is not a supported format. Try again")