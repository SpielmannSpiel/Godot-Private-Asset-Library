import os

import git
from git import Repo, InvalidGitRepositoryError
from inc.ProjectGodotFile import ProjectGodotFile


class Project:

    def __init__(self):
        self.name = ""
        self.directory = ""
        self.full_path = ""
        self.version = ""
        self.last_change = ""
        self.is_valid = False
        self.repo: Repo | None = None
        self.godot_file: ProjectGodotFile | None = None

    def load_from_path(self, full_path):
        self.full_path = full_path
        self.directory = os.path.dirname(full_path)
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

