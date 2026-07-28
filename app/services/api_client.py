import os
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.utils.rate_limiter import RateLimiter
from app.utils.logger import logger

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
BASE_URL = "https://maps.googleapis.com/maps/api/place"
RATE_LIMIT_MAX_CALLS = int(os.getenv("RATE_LIMIT_MAX_CALLS", 10))
RATE_LIMIT_PERIOD = float(os.getenv("RATE_LIMIT_PERIOD", 1.0))
rate_limiter = RateLimiter(max_calls=RATE_LIMIT_MAX_CALLS, period=RATE_LIMIT_PERIOD)

class APIClient:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def search_place(self, query: str):
        await rate_limiter.wait_if_needed()
        url = f"{BASE_URL}/findplacefromtext/json?input={query}&inputtype=textquery&fields=place_id,website&key={API_KEY}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "OK":
                raise ValueError(f"API error: {data.get('status')}")
            return data["candidates"][0] if data["candidates"] else None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def get_place_details(self, query: str):
        await rate_limiter.wait_if_needed()
        search_result = await self.search_place(query)
        if not search_result:
            return {}
        place_id = search_result["place_id"]
        url = f"{BASE_URL}/details/json?place_id={place_id}&fields=formatted_phone_number,website&key={API_KEY}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get("status") != "OK":
                raise ValueError(f"API error: {data.get('status')}")
            return data.get("result", {})

api_client = APIClient()