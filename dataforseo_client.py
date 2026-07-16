"""
dataforseo_client.py
====================
Capa de datos de keywords para los agentes de Nodarishub (Blog Agent / SEO Agent).

Usa DataForSEO Labs API, que trabaja SOLO a nivel país -- exactamente lo que
necesitamos para PYS y Arcade Motors (México nacional) y Nodarishub Ecuador.
Si algún día se necesita SEO local (ciudad), NO es este módulo: es Keywords Data
API (location_code de ciudad) + SERP API (coordenadas / local pack).

Requisitos:
    pip install requests

Variables de entorno (Railway):
    DATAFORSEO_USERNAME=tu_api_login
    DATAFORSEO_PASSWORD=tu_api_password
    NODARIS_EC_DOMAIN=nodarishub.com   # opcional, ajusta al dominio real

Uso rápido:
    from dataforseo_client import DataForSEOClient, MARKETS

    cli = DataForSEOClient()
    temas = cli.blog_topics("pys", ["péptidos", "bpc 157", "suplementos deportivos"])
    print(cli.total_cost)  # USD gastados en esta corrida
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

import requests
from requests.auth import HTTPBasicAuth

log = logging.getLogger(__name__)

BASE_URL = "https://api.dataforseo.com"
STATUS_OK = 20000
MAX_LIMIT = 1000  # tope duro de Labs por request
DEFAULT_TIMEOUT = 90
MAX_RETRIES = 3  # DataForSEO devuelve 403 intermitente (throttle/WAF), no error real de auth
RETRY_BACKOFF = 1.5  # segundos, se duplica en cada intento


# --------------------------------------------------------------------------- #
# Mercados
# --------------------------------------------------------------------------- #
# location_code = 2000 + código ISO 3166-1 numérico  (MX=484 -> 2484, EC=218 -> 2218)
# Verifica la lista completa gratis (cost: 0):
#   GET https://api.dataforseo.com/v3/dataforseo_labs/locations_and_languages


@dataclass(frozen=True)
class Market:
    slug: str
    name: str
    target: str  # dominio sin https:// ni www
    location_code: int
    language_code: str
    competitors: tuple[str, ...] = field(default_factory=tuple)


MARKETS: dict[str, Market] = {
    "pys": Market(
        slug="pys",
        name="Péptidos y Suplementos",
        target="peptidosysuplementos.mx",
        location_code=2484,  # México
        language_code="es",
        competitors=("exomapeptides.mx",),
    ),
    "arcade": Market(
        slug="arcade",
        name="Arcade Motors MX",
        target="arcademotorsmx.com",
        location_code=2484,  # México
        language_code="es",
        # vehiculos.mercadolibre.com.mx: subdominio dedicado a autos de ML,
        # comparable en modelo de negocio (marketplace comprador-vendedor).
        # Kavak descartado -- compra/vende inventario propio, no es marketplace.
        # segundamano.mx descartado -- dado de baja 2023, redirige a Inmuebles24.
        # Facebook Marketplace descartado -- sin huella SEO indexable (app/login).
        # Verificado 2026-07-15.
        competitors=("vehiculos.mercadolibre.com.mx",),
    ),
    "nodaris_ec": Market(
        slug="nodaris_ec",
        name="Nodarishub Ecuador",
        target=os.getenv("NODARIS_EC_DOMAIN", "nodarishub.com"),
        location_code=2218,  # Ecuador
        language_code="es",
        competitors=(),
    ),
}


def get_market(market: str | Market) -> Market:
    if isinstance(market, Market):
        return market
    try:
        return MARKETS[market]
    except KeyError:
        raise ValueError(f"Mercado desconocido: {market!r}. Opciones: {list(MARKETS)}")


class DataForSEOError(RuntimeError):
    pass


# --------------------------------------------------------------------------- #
# Cliente
# --------------------------------------------------------------------------- #
class DataForSEOClient:
    """Wrapper mínimo sobre DataForSEO Labs. Todos los endpoints son /live."""

    def __init__(
        self,
        login: str | None = None,
        password: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        login = login or os.getenv("DATAFORSEO_USERNAME")
        password = password or os.getenv("DATAFORSEO_PASSWORD")
        if not login or not password:
            raise DataForSEOError(
                "Faltan credenciales: define DATAFORSEO_USERNAME y DATAFORSEO_PASSWORD"
            )
        self.timeout = timeout
        self.total_cost = 0.0  # USD acumulados en esta instancia
        self._session = requests.Session()
        self._session.auth = HTTPBasicAuth(login, password)
        self._session.headers.update({"Content-Type": "application/json"})

    def _post_with_retry(self, path: str, task: dict[str, Any]) -> requests.Response:
        """POST con reintento: DataForSEO da 403 intermitente (throttle/WAF),
        no un rechazo real de credenciales -- verificado 2026-07-15 corriendo
        la misma llamada repetida sin cambios."""
        backoff = RETRY_BACKOFF
        for attempt in range(1, MAX_RETRIES + 1):
            resp = self._session.post(f"{BASE_URL}{path}", json=[task], timeout=self.timeout)
            if resp.status_code != 403 or attempt == MAX_RETRIES:
                resp.raise_for_status()
                return resp
            log.warning("%s -> 403 (intento %d/%d), reintentando en %.1fs",
                        path, attempt, MAX_RETRIES, backoff)
            time.sleep(backoff)
            backoff *= 2
        raise DataForSEOError(f"{path} -> 403 tras {MAX_RETRIES} intentos")  # pragma: no cover

    # ---------------------------- núcleo HTTP ---------------------------- #
    def _post(self, path: str, task: dict[str, Any]) -> list[dict[str, Any]]:
        task = {k: v for k, v in task.items() if v is not None}
        resp = self._post_with_retry(path, task)
        payload = resp.json()

        if payload.get("status_code") != STATUS_OK:
            raise DataForSEOError(
                f"{path} -> {payload.get('status_code')}: {payload.get('status_message')}"
            )

        cost = payload.get("cost") or 0.0
        self.total_cost += cost

        tasks = payload.get("tasks") or []
        if not tasks:
            return []
        t = tasks[0]
        if t.get("status_code") != STATUS_OK:
            raise DataForSEOError(
                f"{path} task -> {t.get('status_code')}: {t.get('status_message')}"
            )

        results = t.get("result") or []
        items = (results[0] or {}).get("items") or [] if results else []
        log.info("%s -> %d items | costo $%.5f | acumulado $%.5f",
                 path, len(items), cost, self.total_cost)
        return items

    # -------------------------- normalización ---------------------------- #
    @staticmethod
    def _flatten(item: dict[str, Any]) -> dict[str, Any]:
        """Aplana un item de Labs. Algunos endpoints anidan todo en keyword_data."""
        kd = item.get("keyword_data") or item
        info = kd.get("keyword_info") or {}
        props = kd.get("keyword_properties") or {}
        intent = (kd.get("search_intent_info") or {}).get("main_intent")
        serp = kd.get("serp_info") or {}
        rank = (item.get("ranked_serp_element") or {}).get("serp_item") or {}
        return {
            "keyword": kd.get("keyword"),
            "volume": info.get("search_volume"),
            "cpc": info.get("cpc"),
            "competition": info.get("competition_level"),
            "difficulty": props.get("keyword_difficulty"),
            "intent": intent,
            "serp_results": serp.get("se_results_count"),
            "position": rank.get("rank_absolute"),
            "url": rank.get("url"),
        }

    def _clean(self, items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        rows = [self._flatten(i) for i in items]
        return [r for r in rows if r["keyword"]]

    # ------------------------- endpoints de Labs ------------------------- #
    def keyword_ideas(
        self,
        market: str | Market,
        seeds: Sequence[str],
        limit: int = 100,
        min_volume: int = 10,
    ) -> list[dict[str, Any]]:
        """Keywords de la misma categoría que las semillas. Hasta 200 semillas."""
        m = get_market(market)
        items = self._post(
            "/v3/dataforseo_labs/google/keyword_ideas/live",
            {
                "keywords": list(seeds),
                "location_code": m.location_code,
                "language_code": m.language_code,
                "filters": [["keyword_info.search_volume", ">", min_volume]],
                "order_by": ["keyword_info.search_volume,desc"],
                "limit": min(limit, MAX_LIMIT),
            },
        )
        return self._clean(items)

    def keyword_suggestions(
        self,
        market: str | Market,
        seed: str,
        limit: int = 100,
        only_questions: bool = False,
    ) -> list[dict[str, Any]]:
        """Long-tail que CONTIENE la semilla. only_questions -> filtra 'cómo/qué/por qué'."""
        m = get_market(market)
        filters: list[Any] = [["keyword_info.search_volume", ">", 0]]
        if only_questions:
            filters = [
                ["keyword", "like", "%cómo%"], "or",
                ["keyword", "like", "%como%"], "or",
                ["keyword", "like", "%qué%"], "or",
                ["keyword", "like", "%que es%"], "or",
                ["keyword", "like", "%para que%"],
            ]
        items = self._post(
            "/v3/dataforseo_labs/google/keyword_suggestions/live",
            {
                "keyword": seed,
                "location_code": m.location_code,
                "language_code": m.language_code,
                "include_serp_info": True,
                "filters": filters,
                "order_by": ["keyword_info.search_volume,desc"],
                "limit": min(limit, MAX_LIMIT),
            },
        )
        return self._clean(items)

    def related_keywords(
        self,
        market: str | Market,
        seed: str,
        depth: int = 2,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Del bloque 'búsquedas relacionadas' del SERP. OJO: filtros van anidados."""
        m = get_market(market)
        items = self._post(
            "/v3/dataforseo_labs/google/related_keywords/live",
            {
                "keyword": seed,
                "location_code": m.location_code,
                "language_code": m.language_code,
                "depth": depth,
                "filters": [["keyword_data.keyword_info.search_volume", ">", 10]],
                "limit": min(limit, MAX_LIMIT),
            },
        )
        return self._clean(items)

    def keywords_for_site(
        self,
        market: str | Market,
        target: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Keywords relevantes para un dominio (por categoría, no por ranking)."""
        m = get_market(market)
        items = self._post(
            "/v3/dataforseo_labs/google/keywords_for_site/live",
            {
                "target": target or m.target,
                "location_code": m.location_code,
                "language_code": m.language_code,
                "include_serp_info": True,
                "include_subdomains": True,
                "order_by": ["keyword_info.search_volume,desc"],
                "limit": min(limit, MAX_LIMIT),
            },
        )
        return self._clean(items)

    def ranked_keywords(
        self,
        market: str | Market,
        target: str | None = None,
        limit: int = 500,
        max_position: int = 20,
    ) -> list[dict[str, Any]]:
        """Keywords donde el dominio YA rankea, con posición y URL."""
        m = get_market(market)
        items = self._post(
            "/v3/dataforseo_labs/google/ranked_keywords/live",
            {
                "target": target or m.target,
                "location_code": m.location_code,
                "language_code": m.language_code,
                "filters": [
                    ["ranked_serp_element.serp_item.rank_absolute", "<=", max_position]
                ],
                "order_by": ["keyword_data.keyword_info.search_volume,desc"],
                "limit": min(limit, MAX_LIMIT),
            },
        )
        return self._clean(items)

    def bulk_keyword_difficulty(
        self, market: str | Market, keywords: Sequence[str]
    ) -> dict[str, Any]:
        """KD (0-100) para hasta 1,000 keywords en una sola llamada."""
        m = get_market(market)
        items = self._post(
            "/v3/dataforseo_labs/google/bulk_keyword_difficulty/live",
            {
                "keywords": list(keywords)[:MAX_LIMIT],
                "location_code": m.location_code,
                "language_code": m.language_code,
            },
        )
        return {i.get("keyword"): i.get("keyword_difficulty") for i in items}

    def search_intent(
        self, market: str | Market, keywords: Sequence[str]
    ) -> dict[str, str]:
        """Intención (informational / commercial / transactional / navigational)."""
        m = get_market(market)
        items = self._post(
            "/v3/dataforseo_labs/google/search_intent/live",
            {
                "keywords": list(keywords)[:MAX_LIMIT],
                "language_code": m.language_code,
            },
        )
        out: dict[str, str] = {}
        for i in items:
            kw = i.get("keyword")
            intent = (i.get("keyword_intent") or {}).get("label")
            if kw and intent:
                out[kw] = intent
        return out

    # ------------------------ flujos compuestos -------------------------- #
    def content_gap(
        self,
        market: str | Market,
        competitor: str | None = None,
        limit: int = 500,
        max_difficulty: int = 35,
    ) -> list[dict[str, Any]]:
        """
        Keywords donde el competidor rankea top-20 y nosotros no aparecemos.
        Dos llamadas + resta en Python (más predecible que confiar en un solo
        endpoint de intersección).

        Filtra por max_difficulty: sin esto, el gap contra un competidor mucho
        más grande sale dominado por nombres de marca con dificultad
        inalcanzable (ej. Arcade vs Kavak: "toyota" KD 89, "honda" KD 42) --
        verificado con datos reales 2026-07-15.
        """
        m = get_market(market)
        rival = competitor or (m.competitors[0] if m.competitors else None)
        if not rival:
            raise ValueError(f"{m.slug} no tiene competidores configurados")

        mine = {r["keyword"] for r in self.ranked_keywords(m, limit=limit)}
        theirs = self.ranked_keywords(m, target=rival, limit=limit)
        gap = [
            r for r in theirs
            if r["keyword"] not in mine
            and (r["difficulty"] is None or r["difficulty"] <= max_difficulty)
        ]
        gap.sort(key=lambda r: r["volume"] or 0, reverse=True)
        log.info("content_gap %s vs %s -> %d oportunidades", m.target, rival, len(gap))
        return gap

    def blog_topics(
        self,
        market: str | Market,
        seeds: Sequence[str],
        limit: int = 200,
        min_volume: int = 20,
        max_difficulty: int = 35,
    ) -> list[dict[str, Any]]:
        """
        Lo que consume el Blog Agent: keywords informacionales, con volumen real
        y KD alcanzable para un dominio joven. Ordenadas por volumen.

        Usa keyword_suggestions (long-tail que CONTIENE la semilla) en vez de
        keyword_ideas (categorización de Google Ads) porque para semillas de
        nicho (ej. "bpc 157") keyword_ideas cae a una categoría genérica y
        devuelve resultados sin relación -- verificado con datos reales de PYS
        el 2026-07-15.
        """
        seen: dict[str, dict[str, Any]] = {}
        for seed in seeds:
            for k in self.keyword_suggestions(market, seed, limit=limit):
                if k["keyword"] not in seen:
                    seen[k["keyword"]] = k

        topics = [
            k for k in seen.values()
            if (k["volume"] or 0) >= min_volume
            and (k["difficulty"] is None or k["difficulty"] <= max_difficulty)
            and k["intent"] in (None, "informational")
        ]
        topics.sort(key=lambda r: r["volume"] or 0, reverse=True)
        return topics


# --------------------------------------------------------------------------- #
# Prueba manual:  python dataforseo_client.py pys
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    import json
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    slug = sys.argv[1] if len(sys.argv) > 1 else "pys"
    # Semillas verificadas contra el contenido real de cada sitio (2026-07-15).
    seeds_por_mercado = {
        "pys": ["péptidos", "bpc 157", "suplementos deportivos"],
        # Arcade es marketplace de compra/venta gratis sin comisiones, no agencia
        # de autos -- semillas reflejan ese ángulo, no "camionetas usadas" genérico.
        "arcade": ["vender mi auto", "comprar auto usado", "verificación vehicular"],
        # Nodarishub: mismo dominio para MX y EC, servicios reales del sitio
        # (diseño web a código, SEO, tiendas en línea), no "agencia marketing digital".
        "nodaris_ec": ["diseño de páginas web", "posicionamiento web", "tienda en línea"],
    }

    cli = DataForSEOClient()
    m = get_market(slug)
    print(f"\n== {m.name} | location {m.location_code} | {m.target} ==")

    temas = cli.blog_topics(slug, seeds_por_mercado[slug], limit=50)
    print(json.dumps(temas[:10], ensure_ascii=False, indent=2))
    print(f"\nCosto total de la corrida: ${cli.total_cost:.5f} USD")
