import os


class ProjectGodotFile:

    def __init__(self):
        self.is_valid = False
        self.full_path = ""
        self.entries = {}

    def get_name(self, fallback=""):
        return self.entries.get("config/name", fallback)

    def get_description(self):
        return self.entries.get("config/description", "")

    def get_godot_version(self):
        godot_version = self.entries.get("config/features", "")
        if not godot_version:
            return ""

        # the version row: config/features=PackedStringArray("4.3", "GL Compatibility")
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

                if self._is_row_valid(row):
                    self._set_row_value(row)

        if self.entries:
            self.is_valid = True
            return self.is_valid

        return self.is_valid

    @staticmethod
    def _is_row_valid(row: str):
        # skip empty lines
        if not row:
            return False

        # exclude comments
        if row.startswith(';'):
            return False

        # exclude sections
        if row.startswith('['):
            return False

        # exclude multiline (for now / until proper parsing is made)
        if "=" not in row:
            return False

        return True

    def _set_row_value(self, row: str):
        entry_key, entry_value = row.split('=', 1)

        # is string
        if '"' in entry_value:
            entry_value = entry_value.strip('"')  # remove string quotes
        elif entry_value.isdigit():
            entry_value = int(entry_value)

        self.entries[entry_key] = entry_value
