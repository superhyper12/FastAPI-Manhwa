from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import requests
import re
import httpx

endPoints = APIRouter()

Manhwa_DB = {
    "Manhwa_A" : {"description" : "Postem Morem", "Chapter" :  10, "access": "PREMIUM", "releaseDate": "9/28/2025"}
} # Database layout example

class ManhwaModel(BaseModel):
    description: str # need to add description scraper
    chapters: int # need to check if chapter from scraper is int or char
    access: str 
    recentDate: str

print(Manhwa_DB["Manhwa_A"]["Chapter"])


def RunParser(url):
    response = requests.get(f"https://templetoons.com/comic/{url}") 
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup


def GetParseChapterTag(soupVariable):
    current_chapters = soupVariable.find_all('a', href=re.compile(r'chapter'))
    latest_chapter_tag = current_chapters[0]
    return latest_chapter_tag


def GetLatestChapter(new_chapter):
    latest_chapter = new_chapter.get('href')
    return latest_chapter


def CheckForNewChapter(latest_chapter, stored_chap):  # need to replace print with return chapter int value
    latest_chap = latest_chapter.split("chapter")[-1].strip("-")
    curr_chap = stored_chap.split("chapter")[-1].strip("-")
    if latest_chap > curr_chap:
        stored_chap = latest_chapter
        print("Latest chapter updated!")
        return stored_chap
    else:
        print("No chapter updated")


def stripChapter(latest_chapter):
    latest_chapter = latest_chapter.split("chapter")[-1].strip("-")
    return latest_chapter


def ChapterAccessText(get_chapter):
    child_div = get_chapter.find('div', class_='p-1 h-full flex flex-col justify-center items-start gap-[2px]')
    new_div = child_div.find('span', class_='text-[10px] flex flex-row gap-1 items-center bg-[#ffffff2c] rounded-md py-1 px-2')
    try:
        return f"{new_div.text}"
    except:
        return "FREE"
    

def getManhwaDescription(parse_manhwa): 
    div = parse_manhwa.find('p', class_="text-xs md:text-sm lg:text-normal")
    return f"{div.text}"

def CheckForNewChapter(latest_chapter, stored_chap):
    latest_chap = latest_chapter.split("chapter")[-1].strip("-")
    curr_chap = stored_chap.split("chapter")[-1].strip("-")
    if latest_chap > curr_chap:
        stored_chap = latest_chapter
        return stored_chap, "New Chapter!"
    else:
        return stored_chap, "No Chapter updated"


@endPoints.get("/parse")
async def run_parser(manhwa_name: str):
    soup = RunParser(manhwa_name)
    return {"html": str(soup)}


@endPoints.get("/latest-chapter")
async def get_latest_Chapter(manhwa_name):
    return {"latest-chapter": stripChapter(GetLatestChapter(GetParseChapterTag(RunParser(manhwa_name))))}
    

@endPoints.get("/chapter-access-status")
async def get_chapter_access_status(manhwa_name):
    return{"access": ChapterAccessText(GetParseChapterTag(RunParser(manhwa_name)))}


@endPoints.get("/manhwa-description") 
async def get_manhwa_description(manhwa_name: str):
    return {"description": getManhwaDescription(RunParser(manhwa_name))}


@endPoints.get("/get-list-db")
async def get_all_webtoon():
    return Manhwa_DB


@endPoints.post("/create-manhwa")
async def create_manhwa(manhwa_name):
    if manhwa_name in Manhwa_DB:
        return {"error": "Already exists"}
    Manhwa_DB[manhwa_name] = ManhwaModel(
        description= getManhwaDescription(RunParser(manhwa_name)),
        chapters= stripChapter(GetLatestChapter(GetParseChapterTag(RunParser(manhwa_name)))),
        access= ChapterAccessText(GetParseChapterTag(RunParser(manhwa_name))),
        recentDate="MM/DD/YEAR"
    ).dict()
    return {"id": manhwa_name, "data": Manhwa_DB[manhwa_name]}
        
@endPoints.delete("/delete-manhwa")
async def delete_manhwa(manhwa_name):
    if manhwa_name in Manhwa_DB:
        del Manhwa_DB[manhwa_name]
        return{"message": f"Item {manhwa_name} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@endPoints.patch("/check-new-chapter") #need to the database chapter 
async def check_for_new_chapter(manhwa_name):  
    if manhwa_name in Manhwa_DB:
        stored_chapter = Manhwa_DB[manhwa_name]["Chapter"]

        latest_chapter = (GetLatestChapter(GetParseChapterTag(RunParser(manhwa_name))))

        updated_chapter, message = CheckForNewChapter(latest_chapter, stored_chapter)

        Manhwa_DB[manhwa_name]["Chapter"] = updated_chapter

        return{f"{message}": f"{updated_chapter}"}
    else:
        return{"message": "manhwa does not exist in Database"}











        




