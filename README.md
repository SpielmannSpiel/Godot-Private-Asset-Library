# Godot Private Asset Library

This is a local and private asset library for the Godot game engine.  
It is a simple web application that allows you to host your own asset library on your machine.  
Clone/place your godot asset into the `godot_assets` folder, run the server and import them into your Godot project via the asset library.    

## Setup

* Clone the repository 
* Clone/place your Godot assets in the `godot_assets` folder
  * They should follow the [Godot Asset Library standards](https://docs.godotengine.org/en/stable/community/asset_library/submitting_to_assetlib.html) for best experience 
  * They don't have to be git-repositories and can be just plain folders, but should be for best experience
* Install / Run the server
  * [Locally](#Locally)
  * [With Docker](#Docker)
* Open your browser and navigate to http://127.0.0.1:8080 to validate all is running correctly
* Setup your Godot instance to use your local asset library
  * Open a/the project in Godot where you want the assets to be imported to
    * (the setting is global for all projects, but then you can use it instantly)
  * Go to `Editor -> Editor Settings -> General (tab) -> Asset Library -> Available Urls -> Dictionary`
    * `New Key`: `Library Name` (e.g. `Local Asset Library`)
    * `New Value`: `Library URL` (e.g. `http://127.0.0.1:8080/api`)


![Open Editor Settings](/github_assets/add_asset_library_1.png "Open Editor Settings")
![Open Dictionary](/github_assets/add_asset_library_2.png "Open Dictionary")
![Add type String](/github_assets/add_asset_library_3.png "Add type String")
![Add Key-Value pair](/github_assets/add_asset_library_4.png "Add Key-Value pair")


### Locally

* Optionally create a virtual environment with `python -m venv .venv`
  * Activate the virtual environment with
    * `source .venv/bin/activate` (Mac/Linux) 
    * or `.venv\Scripts\activate` (Windows)
* Install the requirements with `pip install -r requirements.txt`
* Run the server with `python main.py`

### Docker

Run from Docker Hub
```bash
docker compose up
```

Run/build locally
```bash
docker compose -f docker-compose-local.yml up
```
Rebuild local container
```bash
docker compose -f docker-compose-local.yml build godot_asset_library
```

## WARNING

This was **NEVER MEANT** to be run on the open Internet. It has no access control whatsoever.  
It is build to run either on your local machine or your private Network.  
Running it exposed to the Internet is your responsibility to make it secure!

## Licenses & Credits

* Loading Spinner: https://pixabay.com/gifs/load-loading-process-wait-delay-37/

## links

* cross-link GitHub / DockerHub
* Godot assets formats: https://docs.godotengine.org/en/stable/community/asset_library/submitting_to_assetlib.html
* Godot asset library API: https://github.com/godotengine/godot-asset-library/blob/master/API.md#api-get-configure
* Inspiration: https://github.com/christinoleo/godot-custom-assetlib/tree/master / https://github.com/christinoleo/godot-custom-assetlib/tree/master/backend
* Local Documentation: http://127.0.0.1:8080/docs
