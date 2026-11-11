from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl, field_validator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


class LinkInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl

    @field_validator("name", mode="before")
    @classmethod
    def clean_name(cls, value):
        return value.strip() if isinstance(value, str) else value


@app.post("/links")
def create_link(link: LinkInput):
    return {
        "name": link.name,
        "url": str(link.url),
    }