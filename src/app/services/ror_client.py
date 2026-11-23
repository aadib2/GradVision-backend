import httpx

ROR_URL = "https://api.ror.org/v2/organizations"


async def search_organizations(name: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            ROR_URL,
            params={"query": name},
        )
        response.raise_for_status()
        return response.json().get("items", [])


async def get_organization(ror_id: str) -> dict:
    ror_identifier = ror_id.rstrip("/").split("/")[-1]

    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(
            f"{ROR_URL}/{ror_identifier}"
        )
        response.raise_for_status()
        return response.json()