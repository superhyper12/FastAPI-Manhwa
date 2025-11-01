from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from routes_function import *

from pydantic import BaseModel, Field

from Manhwa_DB import Manhwa_DB, ManhwaModel

endPoints = APIRouter()


@endPoints.patch("/manhwas/{manhwa_id}/update-chapter")
async def change_manhwa_chapter(manhwa_name: str, Chapter_val: int):
    if manhwa_name not in Manhwa_DB:
        raise HTTPException(status_code=404, detail="Manhwa not found")
    else:
        Manhwa_DB[manhwa_name]["chapters"] = Chapter_val
        return{"Chapter is changed!"}


@endPoints.get("/run-parser")
async def run_parser(manhwa_name: str):
    soup = RunParser(manhwa_name)
    return {"html": str(soup)}


@endPoints.get("/manhwa/{manhwa_id}/latest-chapter")
async def get_manhwa_latest_chapter(manhwa_name):
    return {"latest-chapter": stripChapter(GetLatestChapter(GetParseChapterTag(RunParser(manhwa_name))))}
    

@endPoints.get("/manhwa/{manhwa_id}/chapter-access")
async def get_chapter_access_status(manhwa_name):
    return{"access": ChapterAccessText(GetParseChapterTag(RunParser(manhwa_name)))}


@endPoints.get("/manhwa/{manhwa_id}/description") 
async def get_manhwa_description(manhwa_name: str):
    return {"description": getManhwaDescription(RunParser(manhwa_name))}


@endPoints.get("/manhwas")
async def get_all_manhwa():
    return Manhwa_DB


@endPoints.post("/manhwas/{manhwa_id}/create")
async def create_manhwa(manhwa_name):
    if manhwa_name in Manhwa_DB:
        raise HTTPException(status_code=400, detail="Manhwa already exists")
    Manhwa_DB[manhwa_name] = ManhwaModel(
        description= getManhwaDescription(RunParser(manhwa_name)),
        chapters= stripChapter(GetLatestChapter(GetParseChapterTag(RunParser(manhwa_name)))),
        access= ChapterAccessText(GetParseChapterTag(RunParser(manhwa_name))),
        recentDate="MM/DD/YEAR"
    ).dict()
    return {"id": manhwa_name, "data": Manhwa_DB[manhwa_name]}

        
@endPoints.delete("/manhwas/{manhwa_id}/delete")
async def delete_manhwa(manhwa_name):
    if manhwa_name in Manhwa_DB:
        del Manhwa_DB[manhwa_name]
        return{"message": f"Item {manhwa_name} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Manhwa not found")


@endPoints.patch("/manhwas/{manhwa_id}/update-chapter-from-parser")
async def update_manhwa_chapter(manhwa_name: str):
    if manhwa_name not in Manhwa_DB:
        raise HTTPException(status_code=404, detail="Manhwa not found")

    stored_chapter = Manhwa_DB[manhwa_name].get("chapters", 0)

    # get href from parser
    latest_href = GetLatestChapter(GetParseChapterTag(RunParser(manhwa_name)))
    updated_chapter, message = CheckForNewChapter(latest_href, stored_chapter)

    # save updated int
    Manhwa_DB[manhwa_name]["chapters"] = updated_chapter

    return {"message": message, "chapters": updated_chapter}











        




