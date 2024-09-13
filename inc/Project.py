import os
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
        self.version = ""
        self.last_change = ""
        self.zip_date = ""
        self.is_valid = False
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

        self.is_valid = self.is_valid_git_dir()
        if not self.is_valid:
            return self.is_valid

        try:
            self.repo = Repo(self.full_path)
        except InvalidGitRepositoryError:
            self.repo = None
            self.is_valid = False
            return self.is_valid

        self.godot_file = ProjectGodotFile()
        self.godot_file.load_file(self.full_path + "/project.godot")
        self.name = self.godot_file.get_name(self.name)

        self.load_git_data()
        self.zip_date = self.get_zip_date()

        self.is_valid = True
        return self.is_valid

    def is_valid_git_dir(self):
        return os.path.isdir(os.path.join(self.full_path, ".git"))

    def get_authors(self):
        return ", ".join(self.authors)

    def get_godot_version(self):
        return self.godot_file.get_godot_version()

    def get_godot_file(self):
        return self.godot_file

    def load_git_data(self):
        self.version = "0.0.0"
        self.authors = set()

        self._load_git_authors()
        self._load_git_urls()
        self._load_git_provider()
        self._load_license()

        for ref in self.repo.refs:
            if hasattr(ref, 'tag'):
                git_tag_ref: git.TagReference = ref
                self.authors.add(git_tag_ref.commit.author.name)
                self.version = git_tag_ref.name
                self.last_change = git_tag_ref.commit.committed_datetime
                break
            else:
                pass
                #git_ref: git.Reference = ref
                #self.authors.add(git_ref.commit.author.name)
                # self.version = git_ref.commit.hexsha
                # self.last_change = git_ref.commit.committed_datetime

        if self.version == "0.0.0" and self.godot_file.is_valid:
            self.version = self.godot_file.entries.get("config/version", "0.0.0")

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

    def get_zip_date(self):
        if not self.has_zip():
            return ""

        return os.path.getmtime(self.get_zip_path())

    def is_zip_up_to_date(self):
        if not self.has_zip():
            return False

        zip_time = self.get_zip_date()
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
            self.zip_date = self.get_zip_date()
            return
