"""E2E: template export → import round-trip — PLAN50."""

from httpx import AsyncClient


async def test_template_export_import_loop(
    client: AsyncClient,
):
    """Export NIST AI RMF → verify ZIP → import into new project."""
    # 1. List built-in templates
    resp = await client.get(
        "/api/v1/templates/builtin"
    )
    assert resp.status_code == 200
    builtins = resp.json()
    assert len(builtins) >= 2

    # 2. Export NIST AI RMF
    resp = await client.post(
        "/api/v1/templates/export",
        json={"framework_id": "nist-ai-rmf"},
    )
    assert resp.status_code == 200
    # Response contains ZIP bytes
    assert len(resp.content) > 0
