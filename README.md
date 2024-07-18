# Discord Bot User Guide

## Adding the Bot to Your Server

To add the bot to your Discord server, click on the following link:

[Add Bot to Server](https://discord.com/oauth2/authorize?client_id=1252695861432156362&permissions=292057840640&integration_type=0&scope=bot)

## Bot Commands

### 1. `!ping`

- **Description**: Use this command to check if the bot is responsive.
- **Usage**: 

- **Response**: The bot will reply with "Pong!" to confirm it's working.

### 2. `!download <url> [format] [tStart] [tEnd]`

- **Description**: This command downloads media from a specified URL. Currently, only YouTube and Twitter videos are supported.
- **Usage**: 

- `<url>`: The URL of the video to download.
- `[format]`: (Optional) The desired format for the downloaded media. Default is `mp4`. Supported formats are:
  - `mp4`
  - `mp3`
  - `mkv`
  - `wav`
  - `mpeg`
  - `gif`
- `[tStart]` and `[tEnd]`: (Optional) Time range for creating a GIF, specified in seconds.
- **Examples**:
- Download a YouTube video in MP4 format:
  ```
  !download https://www.youtube.com/watch?v=example
  ```
- Download a Twitter video in MP3 format:
  ```
  !download https://twitter.com/example/status/example mp3
  ```
- Download a YouTube video and convert it to a GIF from 10 to 20 seconds:
  ```
  !download https://www.youtube.com/watch?v=example gif 10 20
  ```
- **Response**: The bot will download the specified media and send the file in the channel.

## Supported Formats

- Video:
- `mp4`
- `mkv`
- `mpeg`
- `gif`
- Audio:
- `mp3`
- `wav`

## Additional Information

- For converting to a GIF, you can specify a subclip by providing a start and end time (in seconds), which will be used to generate the GIF.
- Example:


If you have any issues or need further assistance, feel free to contact the bot developer.
