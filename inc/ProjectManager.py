import os
import asyncio
from timeit import default_timer
from inc.Project import Project

from config import settings


class ProjectManager:

    def __init__(self):
        self.projects: list[Project] = []

    async def load_projects(self):
        self.projects = []
        # when creating Zips
        #
        # synchron: Loaded 3 projects in 1.1279935000002297 seconds
        #           Loaded 3 projects in 1.126190000000861 seconds
        #
        # async:    Loaded 3 projects in 1.1048000999999203 seconds
        #           Loaded 3 projects in 1.1038666999993438 seconds

        paths_to_projects = []

        start_time = default_timer()
        for dir_name in os.listdir(settings.godot_assets_path_local):
            if dir_name.startswith('.'):
                continue

            full_path = os.path.abspath(os.path.join(settings.godot_assets_path_local, dir_name))

            if os.path.isfile(full_path):
                continue

            paths_to_projects.append(full_path)

        tasks = [asyncio.create_task(self.get_project_from_path(project_path)) for project_path in paths_to_projects]

        for coro in asyncio.as_completed(tasks):
            project = await coro
            self.projects.append(project)

        end_time = default_timer()

        print(f"Loaded {len(self.projects)} projects in {end_time - start_time} seconds")

    def create_zip(self, asset_folder: str):
        for project in self.projects:
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

    @staticmethod
    async def get_project_from_path(full_path: str):
        project = Project()
        if not project.load_from_path(full_path):
            return False

        if not project.is_zip_up_to_date():
            project.create_zip()

        return project

    def add_project(self, full_path):
        project = Project()
        if not project.load_from_path(full_path):
            return False

        if not project.is_zip_up_to_date():
            project.create_zip()

        self.projects.append(project)

        return True

    def get_projects_api_ready(self):
        api_ready = []
        index = 0
        for _ in self.projects:
            api_ready.append(self.get_project_api_ready(index))
            index += 1

        return api_ready

    def get_project_api_ready(self, index: int):
        project = self.projects[index]
        return {
            "asset_id": index,
            "title": project.name,
            "author": project.get_authors(),
            "author_id": "0",
            "category": "Other",
            "category_id": "0",
            "godot_version": project.get_godot_version(),
            "rating": "5",
            "cost": project.license_name,
            "support_level": "testing",
            "icon_url": project.get_icon_url(),
            "version": project.get_combined_version(),
            "version_string": project.get_combined_version(),
            "modify_date": project.last_change,
            # own modifications
            "download_url": project.get_zip_url(),
            "zip_date": project.zip_date,
            "asset_folder": project.directory,
        }

    def get_project_details_api_ready(self, project_index):
        project = self.projects[project_index]

        return {
            "asset_id": project_index,
            "type": "asset",
            "title": project.name,
            "author": project.get_authors(),
            "author_id": "0",
            "version": project.get_combined_version(),
            "version_string": project.get_combined_version(),
            "category": "Other",
            "category_id": "0",
            "godot_version": project.get_godot_version(),
            "rating": "5",
            "cost": project.license_name,
            "description": project.get_godot_file().get_description(),
            "support_level": "testing",
            "download_provider": project.git_repo_provider,
            "download_commit": "master",
            "download_hash": "",  # if blank, verification is skipped
            "browse_url": project.git_page_url,
            "issues_url": "",
            "icon_url": project.get_icon_url(),
            "searchable": "1",
            "modify_date": project.last_change,
            "download_url": project.get_zip_url(),
            "previews": [],
        }
