from scripts import download_twitter_video, download_youtube_video
import json
import os

format = "mp4"

def read_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        
    # Extract the destination and directories
    destination = data[0]["destination"]
    dirs = data[1]
    
    return destination, dirs

def create_dirs(destination,dirs):
    # we want to create the directories in the destination
    for dir in dirs:
        print(f"Creating directory {dir} in {destination}")
        os.makedirs(f"{destination}/{dir}", exist_ok=True)
        print("Directory created")

def download_video(url, video_destination):
    file_name = None
    if "youtube" in url or "youtu.be" in url:
        file_name = download_youtube_video(url, format, video_destination)
    elif "x.com" in url:
        file_name = download_twitter_video(url, video_destination)
    else:
        pass
    return file_name

def main():
    file_path = "download_queue.json"
    destination, dirs = read_json(file_path)
    create_dirs(destination, dirs)
    
    for dir, url in dirs.items():
        file = download_video(url, f"{destination}/{dir}")
        print(f"Downloaded video saved as {file}")

if __name__ == "__main__":
    main()

