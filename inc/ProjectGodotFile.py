import os


class ProjectGodotFile:

    def __init__(self):
        self.is_valid = False
        self.full_path = ""
        self.entries = {}

    def get_godot_version(self):
        godot_version = self.entries.get("config/features", "")
        if not godot_version:
            return ""

        godot_version = godot_version.split('(', 1)[1].split(',', 1)[0].strip('"')

        return godot_version

    def load_file(self, full_path):
        self.full_path = full_path
        self.entries = {}

        if not os.path.isfile(full_path):
            self.is_valid = False
            return self.is_valid

        with open(full_path, 'r') as file:
            for row in file:
                row = row.strip()

                # skip empty lines
                if not row:
                    continue

                # exclude comments
                if row.startswith(';'):
                    continue

                # exclude sections
                if row.startswith('['):
                    continue

                entry_key, entry_value = row.split('=', 1)
                entry_value = entry_value.strip('"')
                self.entries[entry_key] = entry_value

        if self.entries:
            self.is_valid = True
            return self.is_valid

        return self.is_valid
