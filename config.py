from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_version: str = "0.3.0"
    app_name: str = "Godot Private Asset Library"
    godot_assets_path_local: str = "godot_assets"
    cache_path_local: str = "cache"
    zip_path_local: str = f"{cache_path_local}/zip"
    protocol: str = "http"
    domain: str = "127.0.0.1"
    port: int = 8080
    url: str = f"{protocol}://{domain}:{port}"
    allow_infos: bool = True

    def get_frontend_save_context(self):
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "url": self.url
        }

    def get_infos(self):
        # debug infos
        import sys

        return {
            'argv': sys.argv,
            **self.model_dump()
        }


settings = Settings()
