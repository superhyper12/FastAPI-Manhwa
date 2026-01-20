from pydantic import BaseModel, Field
from bs4 import BeautifulSoup, Tag
import requests
import re
import httpx





def get_parser(path: str) -> BeautifulSoup: 
    response = requests.get(f'https://templetoons.com/comic/{path}')
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')
    
def get_manhwa_description(path: str) -> str | None:
    soup = get_parser(path)

    description_tag = soup.find(
        'p',
        class_="text-xs md:text-sm lg:text-normal"
    ) 

    return description_tag.text.strip() if description_tag else None


def get_chapter_tag(path: str):
    soup = get_parser(path)
    chapter_tag = soup.find_all("a", href=re.compile(r"chapter"))

    return chapter_tag[0] if chapter_tag else None

    
def extract_chapter_url(path: str) -> str | None:
    chapter_url = get_chapter_tag(path)
    return chapter_url.get('href') if chapter_url else None


def extract_chapter_number(path: str) -> int:
    href = extract_chapter_url(path)
     
    # Look for 'chapter' optionally a hyphen, then digits
    m = re.search(r'chapter-?(\d+)', href, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))

    # fallback: last sequence of digits in the path
    m2 = re.search(r'(\d+)(?!.*\d)', href)
    if m2:
        return int(m2.group(1))

    raise ValueError(f"Could not find chapter number in '{href}'")
    

def extract_chapter_access(path: str):
    soup = get_chapter_tag(path)

    child_div = soup.find(
        'div', 
        class_='p-1 h-full flex flex-col justify-center items-start gap-[2px]'
        )
    
    if child_div:
        new_div = child_div.find(
            'span', 
            class_='text-[10px] flex flex-row gap-1 items-center bg-[#ffffff2c] rounded-md py-1 px-2'
        )
        return f"{new_div.text}"
    else:
        return "FREE"
    
    

def check_new_chapter(path: str, storedChapter) -> tuple[int, str]: 
    latest_chapter = extract_chapter_number(path)

    if latest_chapter > storedChapter:
        storedChapter = latest_chapter
        return storedChapter, "New Chapter!"
    else:
        return storedChapter, "No Chapter updated"
        


        
