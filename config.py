from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_version: str = "0.4.0"
    app_name: str = "Godot Private Asset Library"
    godot_assets_path_local: str = "godot_assets"
    cache_path_local: str = "cache"
    zip_path_local: str = f"{cache_path_local}/zip"
    protocol: str = "http"
    domain: str = "127.0.0.1"
    port: int = 8080
    allow_infos: bool = True

    def get_url(self) -> str:
        return f"{self.protocol}://{self.domain}:{self.port}"

    def get_frontend_save_context(self):
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "url": self.get_url()
        }

    def get_infos(self):
        # debug infos
        import sys

        return {
            'system': {
                'argv': sys.argv,
            },
            'settings': self.model_dump()
        }


settings = Settings()
