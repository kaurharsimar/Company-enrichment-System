from app.services.api_client import api_client
from app.utils.validators import validate_phone, validate_email
from app.utils.logger import logger

async def discover_contacts(company: str) -> dict:
    try:
        places_result = await api_client.get_place_details(company)
        phone = places_result.get("formatted_phone_number")
        email = None  # Google Places API does not provide email; mark as not found
        return {
            "phone": phone,
            "phone_found": validate_phone(phone) if phone else False,
            "email": email,
            "email_found": False,  # Email not available in Places API
            "source": "Google Places API"
        }
    except Exception as e:
        logger.error(f"Contact discovery failed for {company}: {str(e)}")
        return {"phone": None, "phone_found": False, "email": None, "email_found": False, "source": None}