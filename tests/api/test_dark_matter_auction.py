"""Dark matter title auction — retired from public launch surface."""
from __future__ import annotations

from app.main import app


def test_dark_matter_auction_routes_unmounted():
    paths = {getattr(r, "path", "") for r in app.routes}
    assert "/dark-matter-auction/catalog" not in paths
    assert "/v1/dark-matter-auction/catalog" not in paths


def test_dark_matter_auction_catalog_gone(client):
    res = client.get("/v1/dark-matter-auction/catalog")
    assert res.status_code == 404
