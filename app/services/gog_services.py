import requests
from app.models import GameSearchResult, GameVersionResult
from app.config import settings


def search_gog(query: str) -> list[GameSearchResult]:
    """
    Busca juegos usando la API Catalog V1 de GOG.
    """
    url = settings.GOG_CATALOG_URL
    params = {
        "limit": 20,
        "productType": "in:game",
        "order": "desc:score",
        "query": query,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.gog.com/",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"⚠️ GOG Catalog error: {response.status_code}")
            return []

        data = response.json()
        results = []

        for product in data.get("products", []):
            os_list = product.get("operatingSystems", [])

            game = GameSearchResult(
                id=str(product["id"]),
                title=product["title"],
                platform="GOG",
                supported_os=os_list,
            )
            results.append(game)

        return results

    except Exception as e:
        print(f"❌ Error buscando en GOG: {e}")
        return []


def get_gog_game_version(game_id: str, target_os: str = "windows") -> GameVersionResult:
    """
    Obtiene la versión usando el Content System de GOG.
    """
    # 1. Limpieza y preparación
    clean_id = str(game_id).strip()

    os_param = target_os.lower()
    if os_param == "mac":
        os_param = "osx"

    url = settings.GOG_CONTENT_URL.format(game_id=clean_id, os_param=os_param)

    # 2. HEADERS (CRÍTICO: Sin esto GOG puede devolver 403 Forbidden)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }

    try:
        print(f"📡 Consultando GOG: {url}")  # Debug para ver qué pedimos
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                latest_build = data["items"][0]

                v_str = latest_build.get("version_name", "Desconocida")
                raw_date = latest_build.get("date_published")

                # Limpieza de fecha
                clean_date = None
                if raw_date and isinstance(raw_date, str):
                    clean_date = raw_date.split("T")[0]

                return GameVersionResult(version=v_str, release_date=clean_date)
            else:
                print("⚠️ GOG: Respuesta válida pero sin builds (lista vacía).")
                return GameVersionResult(version="Sin datos", release_date=None)
        else:
            # Aquí veremos si es 404 (ID mal) o 403 (Bloqueado)
            print(f"❌ Error GOG API: Status {response.status_code} para ID {clean_id}")
            return GameVersionResult(version="Error Acceso", release_date=None)

    except Exception as e:
        print(f"❌ Excepción GOG Services: {str(e)}")
        return GameVersionResult(version="Error", release_date=None)
