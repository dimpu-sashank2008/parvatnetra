"""
Unit tests for PARVAT NETRA - GIS Map NER Default View.
"""
import os
import sys
import json
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

NER_8_STATES = {
    "Arunachal Pradesh",
    "Assam",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Sikkim",
    "Tripura"
}

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_geojson_file_exists():
    p1 = os.path.join(os.path.dirname(__file__), "..", "static", "data", "ner_state_boundaries.geojson")
    assert os.path.exists(p1), f"Missing geojson at {p1}"

def test_geojson_endpoint_serves_200(client):
    res = client.get("/static/data/ner_state_boundaries.geojson")
    assert res.status_code == 200, f"Expected HTTP 200 but got {res.status_code}"
    data = json.loads(res.data.decode("utf-8"))
    assert data.get("type") == "FeatureCollection"

def test_all_eight_ner_states_present():
    p = os.path.join(os.path.dirname(__file__), "..", "static", "data", "ner_state_boundaries.geojson")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = data.get("features", [])
    assert len(features) == 8, f"Expected 8 features, found {len(features)}"

    state_names = {feat.get("properties", {}).get("name") for feat in features}
    assert state_names == NER_8_STATES, f"Missing states: {NER_8_STATES - state_names}"

    for feat in features:
        props = feat.get("properties", {})
        name = props.get("name")
        geom = feat.get("geometry", {})
        assert geom.get("type") in ("Polygon", "MultiPolygon"), f"Invalid geom for {name}"
        coords = geom.get("coordinates", [])
        assert len(coords) > 0, f"Empty coords for {name}"

        centroid = props.get("centroid")
        assert centroid is not None and len(centroid) == 2, f"Invalid centroid for {name}"
        c0, c1 = float(centroid[0]), float(centroid[1])
        lat = c0 if 18 <= c0 <= 32 else c1
        lon = c1 if 85 <= c1 <= 100 else c0
        assert 21.0 <= lat <= 30.0, f"Lat out of bounds for {name}: {lat}"
        assert 88.0 <= lon <= 98.0, f"Lon out of bounds for {name}: {lon}"

def test_ner_coordinate_bounding_box():
    p = os.path.join(os.path.dirname(__file__), "..", "static", "data", "ner_state_boundaries.geojson")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_lons = []
    all_lats = []

    def extract(coords):
        if isinstance(coords[0], (int, float)):
            all_lons.append(coords[0])
            all_lats.append(coords[1])
        else:
            for c in coords:
                extract(c)

    for feat in data.get("features", []):
        extract(feat["geometry"]["coordinates"])

    min_lon, max_lon = min(all_lons), max(all_lons)
    min_lat, max_lat = min(all_lats), max(all_lats)

    assert min_lon >= 87.5, f"min_lon {min_lon} too far west"
    assert max_lon <= 98.0, f"max_lon {max_lon} too far east"
    assert min_lat >= 21.5, f"min_lat {min_lat} too far south"
    assert max_lat <= 30.0, f"max_lat {max_lat} too far north"

def test_index_html_ner_configuration():
    idx_path = os.path.join(os.path.dirname(__file__), "..", "templates", "index.html")
    with open(idx_path, "r", encoding="utf-8") as f:
        html = f.read()

    assert "window.NER_BOUNDS = L.latLngBounds([[21.8, 88.0], [29.5, 97.5]]);" in html
    assert "map.fitBounds(window.NER_BOUNDS" in html
    assert "map.createPane('nerStateBoundariesPane');" in html
    assert "map.getPane('nerStateBoundariesPane').style.zIndex = 350;" in html
    assert "nerStateBoundariesLayerGroup" in html
    assert "loadNerStateBoundaries()" in html
    assert "state_boundaries:nerStateBoundariesLayerGroup" in html
    assert "function resetMapToNerBounds()" in html
    assert "resetMapToNerBounds()" in html
    assert 'id="btn-reset-view"' in html
    assert "onCorridorSelectionChanged(top.id, false);" in html
    assert "async function onCorridorSelectionChanged(sectorId, shouldZoom = true)" in html

def test_css_styling_for_ner_labels():
    css_path = os.path.join(os.path.dirname(__file__), "..", "static", "css", "parvat_theme.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    assert ".ner-state-center-label" in css
    assert ".ner-state-label-marker" in css
    assert ".ner-map-zoom-low" in css
