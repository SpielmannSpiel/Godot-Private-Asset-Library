import os

import git
from git import Repo, InvalidGitRepositoryError
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
            self.is_valid = False
            return self.is_valid

        self.godot_file = ProjectGodotFile()
        self.godot_file.load_file(self.full_path + "/project.godot")
        self.load_git_data()
        self.zip_date = self.get_zip_date()

        self.is_valid = True
        return self.is_valid

    def is_valid_git_dir(self):
        return os.path.isdir(os.path.join(self.full_path, ".git"))

    def get_godot_version(self):
        return self.godot_file.get_godot_version()

    def load_git_data(self):
        self.version = "0.0.0"

        for ref in self.repo.refs:
            if hasattr(ref, 'tag'):
                git_tag_ref: git.TagReference = ref
                self.version = git_tag_ref.name
                self.last_change = git_tag_ref.commit.committed_datetime
                break

        if self.version == "0.0.0" and self.godot_file.is_valid:
            self.version = self.godot_file.entries.get("config/version", "0.0.0")

    def get_zip_path(self):
        return os.path.join(settings.zip_path_local, self.directory + ".zip")

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

    def create_zip(self):
        self.zip_date = ""
        if self.repo:
            self.repo.archive(open(self.get_zip_path(), "wb"), format="zip")
            self.zip_date = self.get_zip_date()
            return
