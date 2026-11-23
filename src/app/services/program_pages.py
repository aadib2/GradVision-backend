from datetime import datetime
from bs4 import BeautifulSoup
import httpx


async def fetch_page_text(url: str) -> str:
    headers = {
        "User-Agent": "GradVision academic catalog crawler"
    }

    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        headers=headers,
    ) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "nav", "footer"]):
        element.decompose()

    return soup.get_text(" ", strip=True)