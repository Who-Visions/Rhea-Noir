import requests
from typing import Dict, Any

class WeatherTool:
    """
    A tool to fetch weather data for a given location.
    """
    name = "WeatherTool"
    description = "Gets the current weather conditions for a city."

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city name, e.g. 'London' or 'New York'"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit",
                    "default": "celsius"
                }
            },
            "required": ["location"]
        }

    def execute(self, location: str, unit: str = "celsius") -> str:
        # This is a sample implementation
        api_key = "demo_key" 
        url = f"https://api.weather.com/v1/current?q={location}&key={api_key}&unit={unit}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return f"Weather in {location}: {data['temp']} {unit}, {data['condition']}"
        except Exception as e:
            return f"Error fetching weather: {str(e)}"
