import os
from typing import Annotated

from fastapi import FastAPI
from fastapi.params import Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


from config import settings


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {"message": "Hello World from " + settings.app_name}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    return FileResponse("static/icon.ico")


@app.get('/api/configure')
async def get_config():
    return {
        "categories": [
            {
                "id": "1",
                "name": "2D Tools",
                "type": "0"
            },
            {
                "id": "2",
                "name": "Templates",
                "type": "1"
            },
        ],
        #"token": "...",
        #"login_url": "https://…"
    }


@app.get('/api/asset')
async def list_dummy():
    return {
        "page": 0,
        "pages": 0,
        "page_length": 10,
        "total_items": 1,
        "result": [
            {
                "asset_id": "snake_asset",
                "title": "Snake",
                "author": "test",
                "author_id": "1",
                "category": "2D Tools",
                "category_id": "1",
                "godot_version": "2.1",
                "rating": "5",
                "cost": "GPLv3",
                "support_level": "testing",
                "icon_url": settings.url + "/static/icon.png",
                "version": "1",
                "version_string": "alpha",
                "modify_date": "2018-08-21 15:49:00"
            }
        ]
    }


@app.get('/api/asset/{asset_id}')
async def get_dummy(asset_id: str):
    asset_name = asset_id

    return {
        "asset_id": asset_id,
        "type": "addon",
        "title": "Snake",
        "author": "test",
        "author_id": "1",
        "version": "1",
        "version_string": "alpha",
        "category": "2D Tools",
        "category_id": "1",
        "godot_version": "2.1",
        "rating": "5",
        "cost": "GPLv3",
        "description": "Lorem ipsum…",
        "support_level": "testing",
        "download_provider": "GitHub",
        "download_commit": "master",
        "download_hash": "",  # if blank, verification is skipped
        "browse_url": "",
        "issues_url": "",
        "icon_url": settings.url + "/assets/icon.png",
        "searchable": "1",
        "modify_date": "2018-08-21 15:49:00",
        "download_url": settings.url + f"/api/download/{asset_name}.zip",
        "previews": []
}
