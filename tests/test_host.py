"""
Test the hosting services that this application relies on.
"""

import pytest
import requests


@pytest.mark.integration
def test_extern_status():
    """Get hosting status of twitsave.com"""

    HOST = "https://twitsave.com"
    response = requests.head(HOST)
    assert response.status_code == 200

# Test youtube.com

@pytest.mark.integration
def test_youtube_status():
    """Get hosting status of youtube.com"""

    HOST = "https://youtube.com"
    response = requests.head(HOST)
    assert response.status_code == 301