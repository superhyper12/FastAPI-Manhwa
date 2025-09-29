from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field




Webtoon_DB = {
    1 : {"title": "Webtoon A", "description": "First Chapter", "chapter" : 1},
    2 : {"title": "Webtoon B", "description": "Second Chapter", "chapter": 2}
}


class Webtoon(BaseModel):
    title: str
    description: str
    chapters: int

@endPoints.get("/")
def get_all_webtoon():
    return Webtoon_DB

@endPoints.get("/read_Webtoon_DB")
def read_root(item: int):
    return Webtoon_DB[item]

@endPoints.post("/webtoons")
def create_webtoon(webtoon: Webtoon):
    new_id = max(Webtoon_DB.keys(), default=0) + 1
    Webtoon_DB[new_id] = webtoon.dict()
    return {"id": new_id, "data": Webtoon_DB[new_id]}

@endPoints.delete("/")
def delete_item(item: int):
    if item in Webtoon_DB:
        del Webtoon_DB[item]
        return {"message": f"Item {item} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Item not found")
    
@endPoints.patch("/webtoons/{item_id}")
def update_webtoon(item_id: int, chapter: int, webtoon: Webtoon):
    if item_id in Webtoon_DB:
        new_chapter = chapter
        Webtoon_DB[item_id]["chapter"] = new_chapter
        return {"message": f"Item {item_id} updated successfully.", "data": Webtoon_DB[item_id]}
    else:
        raise HTTPException(status_code=404, detail="Item not found")
  

    


    

