from pydantic import BaseModel, Field
from routes_function import *

Manhwa_DB = {
    "Manhwa_A" : {"description" : "Postem Morem", "Chapter" : 10, "access": "PREMIUM", "releaseDate": "9/28/2025"}
} 

class ManhwaModel(BaseModel):
    description: str | None
    chapters: int | None
    access: str | None

