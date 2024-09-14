import os
import zipfile
from urllib.parse import urlparse


def git_repo_to_page(_git_url):
    if _git_url.startswith('ssh://'):
        _git_url = _git_url.replace('ssh://', 'https://').replace('git@', '')
        parsed_url = urlparse(_git_url)
        netloc = parsed_url.hostname  # Remove port by only using hostname
        _git_url = f"{parsed_url.scheme}://{netloc}{parsed_url.path}"
    elif _git_url.startswith('git@'):
        _git_url = _git_url.replace(':', '/', 1).replace('git@', 'https://')

    if _git_url.endswith('.git'):
        _git_url = _git_url[:-4]

    return _git_url


def get_license_name(full_license_text: str):
    license_lower = full_license_text.lower()

    if "mit" in license_lower:
        return "MIT"

    if "gpl" in license_lower:
        return "GPL"

    if "apache" in license_lower:
        return "Apache"

    if "bsd" in license_lower:
        return "BSD"

    return "Proprietary"


def zip_dir(source_dir, output_filename):
    rel_root = source_dir
    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as _zip:
        for root, dirs, files in os.walk(source_dir):
            relative_path = str(os.path.relpath(root, rel_root))

            # don't include hidden folders
            if relative_path != "." and relative_path.startswith("."):
                continue

            # add directory (needed for empty dirs)
            _zip.write(root, relative_path)

            for file in files:
                filename = str(os.path.join(root, file))
                if os.path.isfile(filename):  # regular files only
                    archived_name = os.path.join(relative_path, file)
                    _zip.write(filename, archived_name)
