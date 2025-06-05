# import pytest
# from unittest.mock import AsyncMock, patch
# from main import download, send_file

# @pytest.mark.asyncio
# async def test_ping_command():
#     mock_ctx = AsyncMock()
#     await download(mock_ctx, args="")
#     mock_ctx.send.assert_called_with("Downloading media...")

# @patch("main.download_media")
# @pytest.mark.asyncio
# async def test_download_command(mock_download_media):
#     mock_download_media.return_value = ("test.mp4", ["test.mp4"])
#     mock_ctx = AsyncMock()
#     args = "https://example.com format=mp4 start=10 end=20 resolution=1920x1080"
#     await download(mock_ctx, args=args)
#     mock_ctx.send.assert_any_call("Downloading media...")
#     mock_ctx.send.assert_any_call("Downloaded successfully")

# @patch("main.send_file")
# @pytest.mark.asyncio
# async def test_send_file(mock_send_file):
#     mock_ctx = AsyncMock()
#     file_name = "test.mp4"
#     await send_file(mock_ctx, file_name)
#     mock_send_file.assert_called_once()
