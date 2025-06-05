import pytest
from unittest.mock import MagicMock, patch
from bot import download
from discord.ext import commands
import asyncio

@pytest.fixture
def mock_ctx():
    ctx = MagicMock()
    ctx.send = MagicMock()
    return ctx

@pytest.mark.asyncio
@patch("bot.VideoDownloader")
@patch("bot.asyncio.to_thread")
async def test_download_command(mock_to_thread, mock_downloader, mock_ctx):
    # Setup mocks
    mock_job = MagicMock()
    mock_downloader.return_value.run_job.return_value = "/path/to/file.mp4"
    mock_to_thread.return_value = "/path/to/file.mp4"
    
    # Test command
    args = "https://youtube.com/watch?v=abc format=mp4 start=5 end=10 resolution=200x200"
    await download(mock_ctx, args=args)
    
    # Verify interactions
    mock_ctx.send.assert_any_call("Downloading media...")
    mock_ctx.send.assert_called_with(file=MagicMock())
    mock_downloader.return_value.run_job.assert_called_once()

@pytest.mark.asyncio
async def test_download_command_errors(mock_ctx):
    # Test invalid input
    with patch("bot.extract_arguments", side_effect=ValueError("Invalid URL")):
        await download(mock_ctx, args="invalid_url")
        mock_ctx.send.assert_called_with("❌ An error occurred: Invalid URL")
    
    # Test processing error
    with patch("bot.VideoDownloader", side_effect=Exception("Processing failed")):
        await download(mock_ctx, args="https://valid.url")
        mock_ctx.send.assert_called_with("❌ An error occurred: Processing failed")