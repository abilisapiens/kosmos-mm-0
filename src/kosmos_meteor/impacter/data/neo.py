"""Helper for the NASA NEO API – returns a dict with orbital elements."""
import httpx
import os
import asyncio

API_KEY = os.getenv("NASA_API_KEY", "H3OI1f68f29fVku1weRGDDyzi74ialdBE9PDe70L")

async def fetch_neo(neo_id: str) -> dict:
    url = f"https://api.nasa.gov/neo/rest/v1/neo/{neo_id}?api_key={API_KEY}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
