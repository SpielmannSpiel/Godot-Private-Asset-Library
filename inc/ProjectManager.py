import os
from inc.Project import Project

from config import settings


class ProjectManager:

    def __init__(self):
        self.projects: list[Project] = []

    def load_projects(self):
        for root, dirs, _ in os.walk(settings.godto_assets_path_local):
            for dir_name in dirs:
                if dir_name.startswith('.'):
                    continue

                full_path = os.path.abspath(os.path.join(root, dir_name))

                project = Project()
                if project.load_from_path(full_path):
                    self.projects.append(project)

    def get_projects_api_ready(self):
        api_ready = []
        index = 0
        for project in self.projects:
            api_ready.append(self.get_project_api_ready(index))
            index += 1

        return api_ready

    def get_project_api_ready(self, index: int):
        project = self.projects[index]
        return {
            "asset_id": index,
            "title": project.name,
            "author": "git",
            "author_id": "1",
            "category": "Other",
            "category_id": "0",
            "godot_version": project.get_godot_version(),
            "rating": "0",
            "cost": "?",
            "support_level": "testing",
            "icon_url": settings.url + "/static/icon.png",
            "version": project.version,
            "version_string": "",
            "modify_date": project.last_change
        }

    def get_project_details_api_ready(self, project_index):
        project = self.projects[project_index]

        return {
            "asset_id": project_index,
            "type": "addon",
            "title": project.name,
            "author": "test",
            "author_id": "1",
            "version": project.version,
            "version_string": "",
            "category": "Other",
            "category_id": "0",
            "godot_version": project.get_godot_version(),
            "rating": "5",
            "cost": "?",
            "description": "Lorem ipsum…",
            "support_level": "testing",
            "download_provider": "GitHub",
            "download_commit": "master",
            "download_hash": "",  # if blank, verification is skipped
            "browse_url": "",
            "issues_url": "",
            "icon_url": settings.url + "/assets/icon.png",
            "searchable": "1",
            "modify_date": project.last_change,
            "download_url": settings.url + f"/api/download/{project_index}.zip",
            "previews": []
        }