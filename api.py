from fastapi import FastAPI
import os
from pydantic import BaseModel, Field, HttpUrl, field_validator

app = FastAPI(
    docs_url='/docs' if os.environ.get('DJANGO_DEBUG', 'true').lower() == 'true' else None,
    redoc_url=None,
    openapi_url=None,
)


class LinkInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl = Field(max_length=2048)

    @field_validator('url')
    @classmethod
    def reject_credentials(cls, value):
        if value.username is not None or value.password is not None:
            raise ValueError('Web addresses must not contain login credentials.')
        return value

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
