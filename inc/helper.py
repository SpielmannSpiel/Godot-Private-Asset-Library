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
