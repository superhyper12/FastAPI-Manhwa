from fastapi import FastAPI, APIRouter
from routes import endPoints

app = FastAPI()
app.include_router(endPoints)
app.add_api_route("/", lambda: {"message": "Welcome to the API!"})


