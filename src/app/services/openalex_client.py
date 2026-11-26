import os
import httpx

OPENALEX_URL = "https://api.openalex.org"
OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY")


def _params(params: dict) -> dict:
    params = dict(params)

    if OPENALEX_API_KEY:
        params["api_key"] = OPENALEX_API_KEY

    # OpenAlex recommends identifying your application.
    params["mailto"] = os.getenv(
        "OPENALEX_EMAIL",
        "your-email@example.com",
    )
    return params


async def get_institution_by_ror(ror_id: str) -> dict:
    ror_identifier = ror_id.rstrip("/").split("/")[-1]

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{OPENALEX_URL}/institutions/ror:{ror_identifier}",
            params=_params({}),
        )
        response.raise_for_status()
        return response.json()


async def search_authors(name: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{OPENALEX_URL}/authors",
            params=_params({
                "search": name,
                "per-page": 10,
            }),
        )
        response.raise_for_status()
        return response.json().get("results", [])


async def get_author_works(openalex_author_id: str) -> list[dict]:
    author_id = openalex_author_id.rstrip("/").split("/")[-1]

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            f"{OPENALEX_URL}/works",
            params=_params({
                "filter": f"authorships.author.id:{author_id}",
                "sort": "publication_date:desc",
                "per-page": 25,
                "select": (
                    "id,title,doi,publication_year,publication_date,"
                    "authorships,topics,abstract_inverted_index,"
                    "primary_location,open_access,cited_by_count"
                ),
            }),
        )
        response.raise_for_status()
        return response.json().get("results", [])