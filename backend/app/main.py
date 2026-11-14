from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Спестослав API", version="0.1.0")


class Category(BaseModel):
    code: str
    name_bg: str
    name_en: str


CATEGORIES = [
    Category(code="food", name_bg="Храни", name_en="Food"),
    Category(code="fuel", name_bg="Горива", name_en="Fuel"),
    Category(code="home", name_bg="Дом", name_en="Home"),
    Category(code="technology", name_bg="Техника", name_en="Technology"),
]


@app.get("/health")
def health():
    return {"status": "ok", "service": "spestoslav-api"}


@app.get("/api/v1/categories", response_model=list[Category])
def categories():
    return CATEGORIES
