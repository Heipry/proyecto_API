import os
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

# Ahora sí usaremos GameSearchResult explícitamente en el modelo de respuesta
from app.config import settings
from app.models import GameSearchResult
from app.services.gog_services import search_gog, get_gog_game_version
from app.services.steam_service import search_steam, get_steam_game_version

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONT_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI(title="GOG vs SteamDB Version Checker")

app.mount("/static", StaticFiles(directory=FRONT_DIR), name="static")


# --- MODELOS DE ENTRADA/SALIDA ---
@app.get("/")
async def read_index():
    # Sirve el HTML cuando entras a la web principal
    return FileResponse(os.path.join(FRONT_DIR, "index.html"))


# Modelo para estructurar la respuesta de búsqueda
class SearchResponse(BaseModel):
    gog: list[GameSearchResult]
    steam: list[GameSearchResult]


class CompareRequest(BaseModel):
    gog_id: str
    steam_id: str
    game_title: str
    gog_os: str = "windows"


class ComparisonResult(BaseModel):
    game_title: str
    gog_version: Optional[str]
    steam_version: Optional[str]
    gog_date: Optional[str]
    steam_date: Optional[str]
    status: str
    difference_days: int
    message: str


# --- UTILIDADES ---


def calculate_date_diff(
    date_gog_str: str | None, date_steam_str: str | None
) -> tuple[int, str]:
    if not date_gog_str or not date_steam_str:
        return 0, "IMPOSIBLE COMPARAR"

    try:
        from datetime import datetime

        d_gog = datetime.strptime(date_gog_str, "%Y-%m-%d")
        d_steam = datetime.strptime(date_steam_str, "%Y-%m-%d")
        diff = (d_steam - d_gog).days

        if abs(diff) <= 90:
            return diff, "AL DÍA"
        elif diff > 90:
            return diff, "DESACTUALIZADO"
        else:  # diff < -90
            return diff, "GOG ADELANTADO"
    except ValueError:
        return 0, "ERROR FORMATO"


# --- ENDPOINTS ---
# Aquí añadimos response_model=SearchResponse para forzar el uso del tipo
@app.get("/search/{query}", response_model=SearchResponse)
def search_games(query: str):
    """
    Busca en GOG y Steam simultáneamente.
    """
    return {"gog": search_gog(query), "steam": search_steam(query)}


@app.post("/compare", response_model=ComparisonResult)
def compare_versions(request: CompareRequest):
    """
    Compara las versiones dados dos IDs.
    """
    # 1. GOG
    gog_data = get_gog_game_version(request.gog_id, request.gog_os)
    if not gog_data:
        raise HTTPException(status_code=404, detail="Error en GOG")

    # 2. Steam
    steam_data = get_steam_game_version(request.steam_id)
    if not steam_data:
        raise HTTPException(status_code=404, detail="Error en SteamDB")

    # 3. Comparar
    days_diff, status_code = calculate_date_diff(
        gog_data.release_date, steam_data.release_date
    )

    msg = "Sin conclusión clara."
    if status_code == "DESACTUALIZADO":
        msg = f"GOG lleva {days_diff} días de retraso respecto a Steam."
    elif status_code == "AL DÍA":
        msg = "¡Versiones sincronizadas!"
    elif status_code == "GOG ADELANTADO":
        msg = "GOG parece tener una versión más nueva."

    return ComparisonResult(
        game_title=request.game_title,
        gog_version=gog_data.version,
        gog_date=gog_data.release_date,
        steam_version=steam_data.version,
        steam_date=steam_data.release_date,
        status=status_code,
        difference_days=days_diff,
        message=msg,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
