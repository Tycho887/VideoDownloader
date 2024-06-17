import os
import requests
from bs4 import BeautifulSoup
import tweepy

# Twitter API credentials

# stored in environment system variables

BEARER_TOKEN = os.environ.get('TwitterBearerToken')

if BEARER_TOKEN is None:
  print("API Key not found in environment variables. Please set it using 'setx TWITTER_API_KEY=YOUR_KEY' (Windows) or export TWITTER_API_KEY=YOUR_KEY (Linux/macOS).")

def get_tweet_id(url):
    """Extract tweet ID from the URL."""
    return url.split('/')[-1].split('?')[0]

def get_video_url(tweet_id):
    """Get the direct video URL from the tweet."""
    client = tweepy.Client(bearer_token=BEARER_TOKEN)

    tweet = client.get_tweet(tweet_id, expansions='attachments.media_keys', media_fields='url')

    if not tweet.includes or 'media' not in tweet.includes:
        print("No video found in the tweet.")
        return None

    media = tweet.includes['media'][0]
    if media.type == 'video':
        return media['url']
    else:
        print("The media is not a video.")
        return None

def download_video(video_url, output_file):
    """Download video from the URL and save it to the specified file."""
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(output_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Video saved as {output_file}")
    else:
        print(f"Failed to download video, status code: {response.status_code}")

def main():
    twitter_video_url = input("Enter the Twitter video URL: ")
    tweet_id = get_tweet_id(twitter_video_url)
    video_url = get_video_url(tweet_id)
    if video_url:
        output_file = 'twitter_video.mp4'
        download_video(video_url, output_file)

if __name__ == "__main__":
    main()
