import pytest
from unittest.mock import Mock, AsyncMock
from ElevationBot import start, start_geocoder, fetch_elevation, ask_location

def test_fetch_elevation():
    # Mount Everest
    assert 9000 >= fetch_elevation(27.99, 86.92) >= 8300
    # K2
    assert 9000 >= fetch_elevation(35.88, 76.51) >= 8300
    # Kangchenjunga
    assert 9000 >= fetch_elevation(27.70, 88.15) >= 8200
    # Random sea point in the Atlantic Ocean
    assert 0 <= fetch_elevation(23.09, -40.31) < 1

def test_start_geocoder():
    # Mount Everest latitude
    assert 28 > start_geocoder("Mount Everest")[0] > 27
    # Mount Everest Llngitude
    assert 87 > start_geocoder("Mount Everest")[1] > 86
    # K2 latitude
    assert 36 > start_geocoder("K2")[0] > 35
    # K2 longitude
    assert 77 > start_geocoder("K2")[1] > 76
    # Kangchenjunga latitude
    assert 28 > start_geocoder("Kangchenjunga")[0] > 27
    # Kangchenjunga longitude
    assert 89 > start_geocoder("Kangchenjunga")[1] > 88

@pytest.mark.asyncio
async def test_start():
    # Create a mock update object with the effective_chat attribute
    mock_update = AsyncMock()
    mock_update.effective_chat.id = 123  # Replace with the expected chat ID

    # Create a mock context object with the bot attribute
    mock_bot = AsyncMock()
    mock_context = AsyncMock()
    mock_context.bot = mock_bot

    # Call the start function with the mock update and context
    await start(mock_update, mock_context)

    # Assert that context.bot.send_message was called with the expected arguments
    mock_bot.send_message.assert_called_once_with(
        chat_id=123,  # Replace with the expected chat ID
        text="I can tell you the elevation at your current location or at a specified location."
        " Use /help to see a list of available commands",
    )
