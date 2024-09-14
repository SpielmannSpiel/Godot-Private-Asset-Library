import os
from datetime import datetime
from urllib.request import pathname2url

import git
from git import Repo, InvalidGitRepositoryError
import inc.helper as helper
from inc.ProjectGodotFile import ProjectGodotFile

from config import settings


class Project:

    def __init__(self):
        self.name = ""
        self.directory = ""
        self.full_path = ""
        self.version_git = ""
        self.version_godot = ""
        self.last_change = None
        self.zip_date = None
        self.is_valid_git = False
        self.is_valid_godot = False
        self.authors = set()
        self.license_name = "Proprietary"
        self.git_remote_url = ""
        self.git_page_url = ""
        self.git_repo_provider = "Unknown"
        self.repo: Repo | None = None
        self.godot_file: ProjectGodotFile | None = None

    def load_from_path(self, full_path):
        self.full_path = full_path
        self.directory = os.path.basename(full_path)
        self.name = os.path.basename(self.full_path)

        self.is_valid_git = self.is_valid_git_dir()

        try:
            self.repo = Repo(self.full_path)
            self.is_valid_git = True
        except InvalidGitRepositoryError:
            self.repo = None
            self.is_valid_git = False

        self.godot_file = ProjectGodotFile()
        self.is_valid_godot = self.godot_file.load_file(self.full_path + "/project.godot")

        if self.is_valid_godot:
            self.load_godot_file_data()

        if self.is_valid_git:
            self.load_git_data()

        if self.is_valid_project():
            self.zip_date = self.get_zip_datetime()

        return self.is_valid_project()

    def is_valid_project(self):
        return self.is_valid_git or self.is_valid_godot

    def is_valid_git_dir(self):
        return os.path.isdir(os.path.join(self.full_path, ".git"))

    def get_authors(self):
        return ", ".join(self.authors)

    def get_godot_version(self):
        return self.godot_file.get_godot_version()

    def get_combined_version(self):
        if self.version_godot and self.version_git:
            return f"{self.version_godot} (git: {self.version_git})"

        if self.version_godot:
            return self.version_godot

        return "git: " + self.version_git

    def get_godot_file(self):
        return self.godot_file

    def load_godot_file_data(self):
        if not self.godot_file.is_valid:
            return

        self.name = self.godot_file.get_name(self.name)
        godot_file_version = self.godot_file.entries.get("config/version", "")
        if godot_file_version:
            self.version_godot = godot_file_version

    def load_git_data(self):
        self.authors = set()

        self._load_git_authors()
        self._load_git_urls()
        self._load_git_provider()
        self._load_license()

        for ref in self.repo.refs:
            if ref.name.startswith('origin/'):
                continue

            if hasattr(ref, 'tag'):
                git_tag_ref: git.TagReference = ref
                self.version_git = git_tag_ref.name
                self.last_change = git_tag_ref.commit.committed_datetime
            else:
                git_ref: git.Reference = ref
                self.version_git = git_ref.commit.hexsha[:6]
                self.last_change = git_ref.commit.committed_datetime

    def _load_git_urls(self):
        self.git_remote_url = ""
        self.git_page_url = ""

        for remote in self.repo.remotes:
            if remote.name == "origin":
                self.git_remote_url = remote.url
                break

        if self.git_remote_url:
            self.git_page_url = helper.git_repo_to_page(self.git_remote_url)

    def _load_git_provider(self):
        if 'gitlab' in self.git_remote_url:
            self.git_repo_provider = "GitLab"
        elif 'github' in self.git_remote_url:
            self.git_repo_provider = "GitHub"

    def _load_git_authors(self):
        for ref in self.repo.refs:
            git_ref: git.Reference = ref
            self.authors.add(git_ref.commit.author.name)

    def get_zip_path(self):
        return os.path.join(settings.zip_path_local, self.directory + ".zip")

    def get_zip_url(self):
        return settings.url + f"/{pathname2url(self.get_zip_path())}"

    def get_icon_url(self):
        return settings.url + f"/api/asset/{self.directory}/icon"

    def has_zip(self):
        return os.path.isfile(self.get_zip_path())

    def get_zip_timestamp(self):
        if not self.has_zip():
            return 0

        return os.path.getmtime(self.get_zip_path())

    def get_zip_datetime(self):
        if not self.has_zip():
            return None

        return datetime.fromtimestamp(os.path.getmtime(self.get_zip_path())).isoformat()

    def is_zip_up_to_date(self):
        if not self.has_zip():
            return False

        zip_time = self.get_zip_timestamp()
        asset_time = os.path.getmtime(self.full_path)

        if self.repo:
            asset_time = self.repo.head.commit.committed_date

        return zip_time >= asset_time

    def _load_license(self):
        license_path = os.path.join(self.full_path, "LICENSE")
        if not os.path.isfile(license_path):
            license_path = os.path.join(self.full_path, "LICENSE.md")

        if not os.path.isfile(license_path):
            return

        self.license_name = helper.get_license_name(open(license_path, "r").read())

    def create_zip(self):
        self.zip_date = ""
        if self.repo:
            self.repo.archive(open(self.get_zip_path(), "wb"), format="zip")
            self.zip_date = self.get_zip_datetime()
            return

        # Fallback
        helper.zip_dir(self.full_path, self.get_zip_path())
        self.zip_date = self.get_zip_datetime()
