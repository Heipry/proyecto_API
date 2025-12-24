import requests
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from app.models import GameSearchResult, GameVersionResult
from app.config import settings


def search_steam(query: str) -> list[GameSearchResult]:
    """
    Busca en Steam usando la API de tienda.
    Devuelve lista de resultados mapeados al modelo común.
    """
    url = settings.STEAM_STORE_URL
    params = {"term": query, "l": "english", "cc": "EN"}

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"error steam search: {response.status_code}")
            return []

        data = response.json()
        results = []

        for item in data.get("items", []):
            # Steam no da info de SOs en esta búsqueda, pero el ID es lo vital
            game = GameSearchResult(
                id=str(item["id"]),
                title=item["name"],
                platform="Steam",
                supported_os=[],
            )
            results.append(game)

        return results

    except Exception as e:
        print(f"excepción búsqueda steam: {e}")
        return []


def get_steam_game_version(game_id: str) -> GameVersionResult:
    """
    Obtiene la fecha del último parche leyendo el RSS de SteamDB.
    URL: https://steamdb.info/api/PatchnotesRSS/?appid=...
    """
    # URL específica del RSS (NO es una API JSON)
    url = settings.STEAM_RSS_URL.format(game_id=game_id)

    # Headers indispensables para evitar bloqueos (WAF/Cloudflare)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"error steamdb rss: {response.status_code}")
            return GameVersionResult(version="Error Acceso", release_date=None)

        # Tratamos la respuesta como XML (RSS Feed)
        # Parseamos el contenido
        try:
            root = ET.fromstring(response.content)
        except ET.ParseError:
            print("Error parseando XML de SteamDB")
            return GameVersionResult(version="Error XML", release_date=None)

        # En RSS 2.0, los items están dentro de <channel>
        channel = root.find("channel")
        if channel is None:
            return GameVersionResult(version="Sin datos", release_date=None)

        items = channel.findall("item")
        if not items:
            return GameVersionResult(version="Sin parches recientes", release_date=None)

        # Tomamos el primer item (el más reciente)
        latest_patch = items[0]

        # Extraemos título
        title_node = latest_patch.find("title")
        title = title_node.text if title_node is not None else "Parche desconocido"

        # Extraemos fecha (pubDate)
        pub_date_node = latest_patch.find("pubDate")
        pub_date_raw = pub_date_node.text if pub_date_node is not None else ""

        clean_date = "N/A"

        # Convertimos la fecha RFC 822 (ej: "Tue, 03 Oct 2023 10:00:00 +0000") a YYYY-MM-DD
        if pub_date_raw:
            try:
                dt_obj = parsedate_to_datetime(pub_date_raw)
                clean_date = dt_obj.strftime("%Y-%m-%d")
            except Exception:
                clean_date = pub_date_raw  # Fallback si falla el parseo

        return GameVersionResult(
            version=title,
            release_date=clean_date,
        )

    except Exception as e:
        print(f"excepción steamdb: {e}")
        return GameVersionResult(version="Error", release_date=None)


# --- ZONA DE PRUEBAS (Main) ---
if __name__ == "__main__":
    print("--- 1. Probando Búsqueda Steam ---")
    busqueda = "Return to Monkey Island"
    juegos = search_steam(busqueda)

    if not juegos:
        print(f"No se encontraron juegos para '{busqueda}'")
    else:
        top_game = juegos[0]
        print(f"Juego encontrado: {top_game.title} (ID: {top_game.id})")

        print(f"\n--- 2. Probando Detalles SteamDB (ID: {top_game.id}) ---")

        # Pasamos el ID obtenido en el paso 1
        detalles = get_steam_game_version(top_game.id)

        print(f"Resultado final Pydantic:")
        print(detalles)
        print(f"Versión/Patch: {detalles.version}")
        print(f"Fecha (Limpia): {detalles.release_date}")
