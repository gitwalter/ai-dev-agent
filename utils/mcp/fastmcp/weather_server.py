"""weather_server.py

This module provides a simple weather server using the FastMCP framework.
It defines a tool for fetching real-time weather information for a specified location
using the OpenWeatherMap API.
"""
from fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    
    import os
    import aiohttp

    OWM_API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY")

    if not OWM_API_KEY:
        return "OpenWeatherMap API key not found. Please set the OPENWEATHERMAP_API_KEY environment variable."

    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={location}&appid={OWM_API_KEY}&units=metric"
    )
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    data = await resp.json()
                    msg = data.get("message", "Unknown error from weather service")
                    return f"Failed to get weather for '{location}': {msg.capitalize()}"
                data = await resp.json()

        weather_main = data["weather"][0]["main"]
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        city = data.get("name", location)

        result = (
            f"The weather in {city} is currently {weather_main} ({weather_desc}). "
            f"Temperature: {temp}°C, feels like {feels_like}°C, humidity: {humidity}%."
        )
        return result
    except Exception as e:
        return f"Error occurred while fetching weather: {e}"
    

if __name__ == "__main__":
    mcp.run(transport="streamable-http")