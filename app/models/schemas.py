import re  # Ajouter cette ligne en haut du fichier
from pydantic import BaseModel, validator
from typing import Optional, Dict

class OrientationProfile(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    preferredSubjects: Optional[str] = None
    fee: Dict[str, Dict[str, Optional[int]]] = {
        "formation": {"min": None, "max": None},
        "logement": {"min": None, "max": None}
    }
    address: Dict[str, Optional[str]] = {
        "city": None,
        "region": None, 
        "country": None
    }
    skills: Optional[str] = None
    desiredFocus: Optional[str] = None
    previousExperience: Optional[str] = None

    @validator('telephone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?[\d\s\-]+$', v):
            return None
        return v

    @validator('email')
    def validate_email(cls, v):
        if v and not re.match(r'[^@]+@[^@]+\.[^@]+', v):
            return None
        return v