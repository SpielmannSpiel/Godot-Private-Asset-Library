import os
import time
import asyncio
from datetime import datetime
from timeit import default_timer

from fastapi import FastAPI
from fastapi import Request
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from readme_renderer import markdown

from config import settings
from inc.ProjectManager import ProjectManager


project_manager = ProjectManager()
asyncio.create_task(project_manager.load_projects())
project_icon_cache = {}

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/github_assets", StaticFiles(directory="github_assets"), name="github_assets")
app.mount("/cache/zip", StaticFiles(directory="cache/zip"), name="cache_zip")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    return templates.TemplateResponse(
        name="pages/home.html",
        request=request,
        context=settings.get_frontend_save_context()
    )


@app.get("/favicon.ico", include_in_schema=False)
async def get_favicon():
    return FileResponse("static/icon.ico")


@app.get("/readme", include_in_schema=False, response_class=HTMLResponse)
async def readme(request: Request):
    return templates.TemplateResponse(
        name="pages/readme.html",
        request=request,
        context={'readme_content': markdown.render(open("README.md").read())}
    )


@app.get('/api/asset/{asset_folder}/icon')
async def get_project_icon(asset_folder: str):
    fallback_icon = "static/icon.png"

    if any(_char in asset_folder for _char in ["/", "\\", "."]):
        return FileResponse(fallback_icon)

    asset_path = os.path.join(settings.godot_assets_path_local, asset_folder)

    if asset_path in project_icon_cache:
        return FileResponse(project_icon_cache[asset_path])

    valid_file_names = ["Icon", "icon"]
    valid_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]

    for file_name in valid_file_names:
        for extension in valid_extensions:
            full_icon_path = os.path.join(asset_path, f"{file_name}{extension}")

            if os.path.isfile(full_icon_path):
                project_icon_cache[asset_path] = full_icon_path
                return FileResponse(full_icon_path)

    # fallback
    project_icon_cache[asset_path] = fallback_icon
    return FileResponse(fallback_icon)


@app.get('/htmlapi/asset/{asset_folder}/create_zip', response_class=HTMLResponse)
async def refresh_projects(asset_folder: str, request: Request):
    return templates.TemplateResponse(
        name="status.html",
        request=request,
        context=(await create_zip(asset_folder)) | {"now": datetime.now(), "title": "Create Zip: " + asset_folder},
    )


@app.get('/api/asset/{asset_folder}/create_zip')
async def create_zip(asset_folder: str):
    return await project_manager.create_zip(asset_folder)


@app.get('/htmlapi/create_all_zips', response_class=HTMLResponse)
async def refresh_projects(request: Request):
    result = await create_all_zips()

    result["message"] = "Created Successfully: " + str(result["creations_successful"])
    result["message"] += "<br />Creations Failed: " + str(result["creations_failed"])

    return templates.TemplateResponse(
        name="status.html",
        request=request,
        context=result | {"now": datetime.now(), "title": "Create All Zips"},
    )


@app.get('/api/create_all_zips')
async def create_all_zips():
    return await project_manager.create_all_zips()


@app.get('/htmlapi/refresh_projects', response_class=HTMLResponse)
async def refresh_projects(request: Request):
    return templates.TemplateResponse(
        name="status.html",
        request=request,
        context=(await refresh_projects()) | {"now": datetime.now(), "title": "Refresh Projects"},
    )


@app.get('/api/refresh_projects')
async def refresh_projects():
    start_time = default_timer()

    project_icon_cache.clear()
    await project_manager.load_projects()

    end_time = default_timer()

    duration = end_time - start_time

    # People tend to NOT notice something did happen when it was too fast
    # and start clicking wildly on a button.
    # This fakes at least 1 second of delay for a human to actually "feel" something did happen.
    if duration < 1:
        time.sleep(1 - duration)

    return {
        "status": "ok",
        "duration": duration
    }


@app.get('/api/configure')
async def get_config():
    # just static since we have no database and godot has no fields for this
    return {
        "categories": [
            {
                "id": "0",
                "name": "Other",
                "type": "0"
            },
        ],
    }


@app.get('/api/asset')
async def list_assets():
    asset_list = []

    for project_ready in project_manager.get_projects_api_ready():
        asset_list.append(project_ready)

    return {
        "page": 0,
        "pages": 0,
        "page_length": len(asset_list),
        "total_items": len(asset_list),
        "result": asset_list
    }


@app.get('/api/html/asset', response_class=HTMLResponse)
async def list_assets_html(request: Request):
    asset_list = []

    for project_ready in project_manager.get_projects_api_ready():
        asset_list.append(project_ready)

    return templates.TemplateResponse(
        name="asset_row.html",
        request=request,
        context={'asset_list': asset_list}
    )


@app.get('/api/asset/{asset_id}')
async def get_project_details(asset_id: int):
    project = project_manager.get_project_details_api_ready(asset_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail=f"Project ID '{asset_id}' not found"
        )

    return project


@app.get('/api/infos')
async def get_infos():
    if not settings.allow_infos:
        raise HTTPException(
            status_code=401,
            detail="allow_infos Deactivated in settings"
        )

    return settings.get_infos()
