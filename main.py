import os
import time
from timeit import default_timer

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from readme_renderer import markdown

from config import settings
from inc.ProjectManager import ProjectManager

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/github_assets", StaticFiles(directory="github_assets"), name="github_assets")
app.mount("/cache/zip", StaticFiles(directory="cache/zip"), name="cache_zip")
templates = Jinja2Templates(directory="templates")

project_manager = ProjectManager()
project_manager.load_projects()
project_icon_cache = {}


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
    if any(_char in asset_folder for _char in ["/", "\\", "."]):
        return FileResponse("static/icon.png")

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
    project_icon_cache[asset_path] = "static/icon.png"
    return FileResponse("static/icon.png")


@app.get('/api/asset/{asset_folder}/create_zip')
async def create_zip(asset_folder: str):
    for project in project_manager.projects:
        if project.directory == asset_folder:
            start_time = default_timer()
            project.create_zip()
            end_time = default_timer()

            duration = end_time - start_time
            return {
                "status": "ok",
                "duration": duration
            }

    return {
        "status": "error",
        "message": "Project not found"
    }

@app.get('/api/refresh_projects')
async def refresh_projects():
    start_time = default_timer()

    project_icon_cache.clear()
    project_manager.load_projects()

    end_time = default_timer()

    duration = end_time - start_time

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
    return project_manager.get_project_details_api_ready(asset_id)
