import os
from inc.Project import Project

from config import settings


class ProjectManager:

    def __init__(self):
        self.projects: list[Project] = []

    def load_projects(self):
        self.projects = []

        for root, dirs, _ in os.walk(settings.godot_assets_path_local):
            for dir_name in dirs:
                if dir_name.startswith('.'):
                    continue

                full_path = os.path.abspath(os.path.join(root, dir_name))
                self.add_project(full_path)

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
