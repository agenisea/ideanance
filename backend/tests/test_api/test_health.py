"""Health endpoint test."""

from httpx import AsyncClient


async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] is True
    assert data["version"] == "0.1.0"
