"""Tests for the Kartverket Stedsnavn connector."""

from unittest.mock import MagicMock, patch

from toponymia.connectors.base import ConnectorResult
from toponymia.connectors.kartverket import _LANGUAGE_MAP, KartverketConnector


def test_kartverket_connector_metadata():
    """Test connector class-level metadata."""
    connector = KartverketConnector()
    assert connector.source_id == "kartverket"
    assert connector.source_name == "Kartverket Stedsnavn"
    assert connector.license == "NLOD-2.0"
    assert connector.coverage_region == "NO"
    assert "geonorge.no" in connector.source_url


def test_kartverket_validation_valid_record():
    """Test validation of a valid Norwegian record."""
    connector = KartverketConnector()
    record = ConnectorResult(
        latitude=59.9139,
        longitude=10.7522,
        name_form="Oslo",
        name_normalized="oslo",
        language_code="nob",
        source_id="kartverket:12345",
    )
    errors = connector.validate(record)
    assert len(errors) == 0


def test_kartverket_validation_outside_norway():
    """Test validation catches coordinates outside Norway."""
    connector = KartverketConnector()
    record = ConnectorResult(
        latitude=48.8566,  # Paris - not in Norway
        longitude=2.3522,
        name_form="Paris",
        name_normalized="paris",
        language_code="nob",
        source_id="kartverket:99999",
    )
    errors = connector.validate(record)
    assert any(e.field == "latitude" for e in errors)
    assert any(e.field == "longitude" for e in errors)


def test_kartverket_validation_empty_name():
    """Test validation catches empty name."""
    connector = KartverketConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="",
        name_normalized="",
        language_code="nob",
        source_id="kartverket:0",
    )
    errors = connector.validate(record)
    assert any(e.field == "name_form" for e in errors)


def test_kartverket_validation_unknown_language():
    """Test validation warns on unrecognized language code."""
    connector = KartverketConnector()
    record = ConnectorResult(
        latitude=60.0,
        longitude=10.0,
        name_form="Test",
        name_normalized="test",
        language_code="zzz",  # Unrecognized
        source_id="kartverket:0",
    )
    errors = connector.validate(record)
    assert any(e.field == "language_code" for e in errors)


def test_kartverket_language_map():
    """Test that language map covers expected codes."""
    assert "nob" in _LANGUAGE_MAP
    assert "nno" in _LANGUAGE_MAP
    assert "sme" in _LANGUAGE_MAP
    assert "smj" in _LANGUAGE_MAP
    assert "sma" in _LANGUAGE_MAP
    assert "fkv" in _LANGUAGE_MAP


def test_kartverket_parse_name_entry():
    """Test parsing a single name entry from the API."""
    connector = KartverketConnector()

    entry = {
        "stedsnummer": 54321,
        "navneobjekttype": "By",
        "representasjonspunkt": {"nord": 63.4305, "ost": 10.3951},
        "kommuner": [{"kommunenummer": "5001", "kommunenavn": "Trondheim"}],
        "skrivemåter": [
            {
                "langnavn": "Trondheim",
                "språk": "nob",
                "navnestatus": "vedtatt",
            },
            {
                "langnavn": "Tråante",
                "språk": "sme",
                "navnestatus": "vedtatt",
            },
        ],
    }

    results = connector._parse_name_entry(entry)
    assert len(results) == 2

    # First result: Norwegian Bokmål
    nob_result = results[0]
    assert nob_result.name_form == "Trondheim"
    assert nob_result.language_code == "nob"
    assert nob_result.latitude == 63.4305
    assert nob_result.longitude == 10.3951
    assert nob_result.is_current is True
    assert nob_result.place_type == "By"
    assert "kartverket:54321" in nob_result.source_id

    # Second result: Northern Sámi
    sme_result = results[1]
    assert sme_result.name_form == "Tråante"
    assert sme_result.language_code == "sme"
    assert sme_result.is_current is True


def test_kartverket_parse_entry_no_coordinates():
    """Test that entries without coordinates are skipped."""
    connector = KartverketConnector()

    entry = {
        "stedsnummer": 99999,
        "navneobjekttype": "Ukjent",
        "skrivemåter": [{"langnavn": "NoCoords", "språk": "nob"}],
    }

    results = connector._parse_name_entry(entry)
    assert len(results) == 0


def test_kartverket_extract_alternatives():
    """Test alternative name extraction."""
    connector = KartverketConnector()

    skrivemaater = [
        {"langnavn": "Tromsø", "språk": "nob"},
        {"langnavn": "Romsa", "språk": "sme"},
        {"langnavn": "Tromssa", "språk": "fkv"},
    ]

    alternatives = connector._extract_alternatives(skrivemaater, "Tromsø")
    assert "sme" in alternatives
    assert "Romsa" in alternatives["sme"]
    assert "fkv" in alternatives
    assert "Tromssa" in alternatives["fkv"]
    # Excluded form not in alternatives
    assert "nob" not in alternatives or "Tromsø" not in alternatives.get("nob", [])


@patch("toponymia.connectors.kartverket.httpx.Client")
def test_kartverket_fetch_pagination(mock_client_class):
    """Test that fetch handles pagination correctly."""
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client

    # Page 1 response
    page1_response = MagicMock()
    page1_response.json.return_value = {
        "metadata": {"totaltAntallTreff": 2, "totaltAntallSider": 2, "side": 1},
        "navn": [
            {
                "stedsnummer": 1,
                "navneobjekttype": "Fjord",
                "representasjonspunkt": {"nord": 61.0, "ost": 7.0},
                "kommuner": [{"kommunenummer": "4601"}],
                "skrivemåter": [
                    {"langnavn": "Sognefjorden", "språk": "nob", "navnestatus": "vedtatt"}
                ],
            }
        ],
    }
    page1_response.raise_for_status = MagicMock()

    # Page 2 response
    page2_response = MagicMock()
    page2_response.json.return_value = {
        "metadata": {"totaltAntallTreff": 2, "totaltAntallSider": 2, "side": 2},
        "navn": [
            {
                "stedsnummer": 2,
                "navneobjekttype": "Elv",
                "representasjonspunkt": {"nord": 59.0, "ost": 10.0},
                "kommuner": [{"kommunenummer": "3005"}],
                "skrivemåter": [{"langnavn": "Glomma", "språk": "nob", "navnestatus": "vedtatt"}],
            }
        ],
    }
    page2_response.raise_for_status = MagicMock()

    mock_client.get.side_effect = [page1_response, page2_response]

    connector = KartverketConnector()
    connector._client = mock_client
    connector._last_request_time = 0.0

    results = list(connector.fetch())
    assert len(results) == 2
    assert results[0].name_form == "Sognefjorden"
    assert results[1].name_form == "Glomma"


def test_kartverket_repr():
    """Test string representation."""
    connector = KartverketConnector()
    repr_str = repr(connector)
    assert "Kartverket" in repr_str or "kartverket" in repr_str
