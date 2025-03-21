from pydantic import BaseModel
from typing import List, Optional

class SuggestionRequest(BaseModel):
    question: str
    infos: Optional[str] = None  # Informations supplémentaires facultatives

class SuggestionResponse(BaseModel):
    suggestions: List[str]
