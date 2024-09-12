from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Godot Private Asset Library"
    godto_assets_path_local: str = "godot_assets"
    protocol: str = "http"
    domain: str = "127.0.0.1"
    port: int = 8080
    url: str = f"{protocol}://{domain}:{port}"

    def get_frontend_save_context(self):
        return {
            "app_name": self.app_name,
            "url": self.url
        }


settings = Settings()
