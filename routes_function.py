from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import requests
import re
import httpx



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



def extract_chapter_number(href: str) -> int:
    
    """
    Extracts the chapter number from strings like:
      - "comic/its-just-business/chapter-92"
      - "/comic/.../chapter92/"
      - "chapter-10"
    Raises ValueError if no number is found.

    """
    if not isinstance(href, str):
        raise ValueError("href must be a string")

    # Look for 'chapter' optionally a hyphen, then digits
    m = re.search(r'chapter-?(\d+)', href, flags=re.IGNORECASE)
    if m:
        return int(m.group(1))

    # fallback: last sequence of digits in the path
    m2 = re.search(r'(\d+)(?!.*\d)', href)
    if m2:
        return int(m2.group(1))

    raise ValueError(f"Could not find chapter number in '{href}'")


def CheckForNewChapter(latest_chapter_href: str, stored_chap) -> tuple[int, str]:
    """
    latest_chapter_href: href string that includes chapter number
    stored_chap: int or str (converted to int)
    Returns: (chapter_int, message)
    """
    try:
        latest_num = extract_chapter_number(latest_chapter_href)
    except ValueError as e:
        # if we can't parse the latest href, keep stored value and return error message
        try:
            curr_num = int(stored_chap)
        except Exception:
            curr_num = stored_chap  # last resort, pass-through
        return curr_num, f"Error parsing latest chapter: {e}"

    try:
        curr_num = int(stored_chap)
    except Exception:
        # if stored value is malformed, prefer latest
        return latest_num, "Stored chapter invalid — using latest chapter"

    if latest_num > curr_num:
        return latest_num, "New Chapter!"
    else:
        return curr_num, "No Chapter updated"
