from pydantic import BaseModel
from typing import Dict, Optional

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
    address: Dict[str, Optional[str]] = {"city": None, "region": None, "country": None}
    skills: Optional[str] = None
    desiredFocus: Optional[str] = None
    previousExperience: Optional[str] = None
