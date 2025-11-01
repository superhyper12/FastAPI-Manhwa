from pydantic import BaseModel, Field


Manhwa_DB = {
    "Manhwa_A" : {"description" : "Postem Morem", "Chapter" : 10, "access": "PREMIUM", "releaseDate": "9/28/2025"}
} 

class ManhwaModel(BaseModel):
    description: str 
    chapters: int 
    access: str 
    recentDate: str

