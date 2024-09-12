from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Godot Private Asset Library"
    git_path_local: str = "git_repos"
    protocol: str = "http"
    domain: str = "127.0.0.1"
    port: int = 8080
    url: str = f"{protocol}://{domain}:{port}"


settings = Settings()
