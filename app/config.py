import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()


class Settings:
    # GOG
    GOG_CATALOG_URL = os.getenv("GOG_CATALOG_URL", "https://catalog.gog.com/v1/catalog")
    GOG_CONTENT_URL = os.getenv("GOG_CONTENT_URL")

    # STEAM
    STEAM_STORE_URL = os.getenv(
        "STEAM_STORE_URL", "https://store.steampowered.com/api/storesearch/"
    )
    STEAM_RSS_URL = os.getenv("STEAM_RSS_URL")


settings = Settings()
