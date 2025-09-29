from bs4 import BeautifulSoup
import requests
import re


curr_chapter = ""
temple_url1 = "impure-reunion" 
temple_url2 = "its-just-business" 
temple_url3 = "trashy-situation-complete-edition"


def RunParser(url):
    response = requests.get(f"https://templetoons.com/comic/{url}") 
    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup

def getManhwaDescription(manhwa_name):
    div = manhwa_name.find('p', class_="text-xs md:text-sm lg:text-normal")
    return f"{div.text}"

def GetParseChapterTag(soupVariable):
    current_chapters = soupVariable.find_all('a', href=re.compile(r'chapter'))
    return current_chapters[0]
    

def GetLatestChapter(new_chapter):
    latest_chapter = new_chapter.get('href')
    return latest_chapter

def ChapterAccessText(get_chapter):
    child_div = get_chapter.find('div', class_='p-1 h-full flex flex-col justify-center items-start gap-[2px]')
    new_div = child_div.find('span', class_='text-[10px] flex flex-row gap-1 items-center bg-[#ffffff2c] rounded-md py-1 px-2')
    try:
        return f"{new_div.text}"
    except:
        return "FREE"

def CheckForNewChapter(latest_chapter, stored_chap):  # need to replace print with return chapter int value
    latest_chap = latest_chapter.split("chapter")[-1].strip("-")
    curr_chap = stored_chap.split("chapter")[-1].strip("-")
    if latest_chap > curr_chap:
        stored_chap = latest_chapter
        print("Latest chapter updated!")
        return stored_chap
    else:
        print("No chapter updated")

def OutputLatestChapter(inputManhwaName):
    GetLatestChapter(GetParseChapterTag(RunParser(inputManhwaName)))



manhwaDescription = getManhwaDescription(RunParser(temple_url3))
print(manhwaDescription)
'''
def PrintOutResult(latest_chapter, current_chapter): # Layout for nested def function
    getWebs = RunParser(latest_chapter)
    y = GetParseChapterTag(getWebs)
    z = GetLatestChapter(y)
    x1 = CheckForNewChapter(z, current_chapter)
    x2 = ChapterAccessText(y)
    print(f"Link: https://templetoons.com/comic/{x1}")
'''


# PrintOutResult(temple_url2, curr_chapter)
