import httpx
from app.services.api_client import api_client
from app.utils.logger import logger


async def detect_website(company: str) -> dict:
    # Guess domains
    domains = [f"{company.replace(' ', '')}.com", f"{company.replace(' ', '')}.in", f"{company.replace(' ', '')}.co.in"]

    for domain in domains:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(f"https://{domain}", timeout=5)
                if response.status_code < 400:
                    return {"website_found": True, "website_url": f"https://{domain}"}
        except:
            continue

    # Fallback to Google Places API search
    try:
        places_result = await api_client.search_place(company)
        if places_result and "website" in places_result:
            return {"website_found": True, "website_url": places_result["website"]}
    except Exception as e:
        logger.error(f"Website detection failed for {company}: {str(e)}")

    return {"website_found": False, "website_url": None}