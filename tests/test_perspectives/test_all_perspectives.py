"""Tests for perspective modules (Milestone 5 + Milestone 12)."""

from uuid import uuid4

from toponymia.perspectives.acoustic import (
    _ACOUSTIC_ELEMENTS,
    AcousticPerspective,
)
from toponymia.perspectives.archaeological import (
    _ARCHAEOLOGICAL_ELEMENTS,
    ArchaeologicalPerspective,
)
from toponymia.perspectives.astronomical import (
    _ASTRONOMICAL_ELEMENTS,
    AstronomicalPerspective,
)
from toponymia.perspectives.base import BasePerspective, Hypothesis
from toponymia.perspectives.colour import (
    _COLOUR_ELEMENTS,
    ColourPerspective,
)
from toponymia.perspectives.ecological import (
    _FAUNA_ELEMENTS,
    _FLORA_ELEMENTS,
    EcologicalPerspective,
)
from toponymia.perspectives.economic import (
    _ECONOMIC_ELEMENTS,
    EconomicPerspective,
)
from toponymia.perspectives.historical import (
    _PERIOD_ELEMENTS,
    HistoricalPerspective,
)
from toponymia.perspectives.hydrological import (
    _HYDRO_ELEMENTS,
    HydrologicalPerspective,
)
from toponymia.perspectives.legal import (
    _LEGAL_ELEMENTS,
    LegalPerspective,
)
from toponymia.perspectives.medicinal import (
    _CARE_ELEMENTS,
    _HEALING_WATER_ELEMENTS,
    _MEDICINAL_PLANT_ELEMENTS,
    MedicinalPerspective,
)
from toponymia.perspectives.migration import (
    _MIGRATION_ELEMENTS,
    MigrationPerspective,
)
from toponymia.perspectives.mortality import (
    _HAZARD_ELEMENTS,
    MortalityPerspective,
)
from toponymia.perspectives.religious import (
    _CULT_ELEMENTS,
    _DEITY_ELEMENTS,
    ReligiousPerspective,
)
from toponymia.perspectives.temporal_cycles import (
    _TEMPORAL_ELEMENTS,
    TemporalPerspective,
)
from toponymia.perspectives.terrain import (
    _TERRAIN_ELEMENTS,
    TerrainFeatures,
    TerrainPerspective,
)

# --- Terrain Perspective ---


class TestTerrainPerspective:
    """Tests for TerrainPerspective."""

    def test_metadata(self):
        p = TerrainPerspective()
        assert p.perspective_id == "terrain"
        assert p.name == "Terrain Correspondence"

    def test_is_base_perspective(self):
        p = TerrainPerspective()
        assert isinstance(p, BasePerspective)

    def test_extract_features(self):
        p = TerrainPerspective()
        features = p.extract_features(uuid4())
        assert "elevation_m" in features
        assert "slope_deg" in features

    def test_generate_hypotheses(self):
        p = TerrainPerspective()
        hypos = p.generate_hypotheses(uuid4())
        assert len(hypos) > 0
        assert all(isinstance(h, Hypothesis) for h in hypos)

    def test_terrain_elements_defined(self):
        assert "berg" in _TERRAIN_ELEMENTS
        assert "dal" in _TERRAIN_ELEMENTS
        assert "nes" in _TERRAIN_ELEMENTS

    def test_classify_terrain_match_berg(self):
        p = TerrainPerspective()
        features = TerrainFeatures(elevation_diff_500m=100.0, slope_deg=15.0)
        matches, confidence = p.classify_terrain_match("berg", features)
        assert matches is True
        assert confidence > 0.5

    def test_classify_terrain_match_flat(self):
        p = TerrainPerspective()
        features = TerrainFeatures(elevation_diff_500m=2.0, slope_deg=1.0)
        matches, confidence = p.classify_terrain_match("flat", features)
        assert matches is True

    def test_classify_terrain_unknown_element(self):
        p = TerrainPerspective()
        features = TerrainFeatures()
        matches, confidence = p.classify_terrain_match("xyz", features)
        assert matches is False
        assert confidence == 0.0


# --- Hydrological Perspective ---


class TestHydrologicalPerspective:
    """Tests for HydrologicalPerspective."""

    def test_metadata(self):
        p = HydrologicalPerspective()
        assert p.perspective_id == "hydrological"

    def test_is_base_perspective(self):
        assert isinstance(HydrologicalPerspective(), BasePerspective)

    def test_extract_features(self):
        features = HydrologicalPerspective().extract_features(uuid4())
        assert "nearest_river_m" in features
        assert "nearest_lake_m" in features

    def test_generate_hypotheses(self):
        hypos = HydrologicalPerspective().generate_hypotheses(uuid4())
        assert len(hypos) == len(_HYDRO_ELEMENTS)

    def test_hydro_elements_defined(self):
        assert "å" in _HYDRO_ELEMENTS
        assert "fjord" in _HYDRO_ELEMENTS
        assert "sjø" in _HYDRO_ELEMENTS


# --- Archaeological Perspective ---


class TestArchaeologicalPerspective:
    """Tests for ArchaeologicalPerspective."""

    def test_metadata(self):
        p = ArchaeologicalPerspective()
        assert p.perspective_id == "archaeological"

    def test_is_base_perspective(self):
        assert isinstance(ArchaeologicalPerspective(), BasePerspective)

    def test_extract_features(self):
        features = ArchaeologicalPerspective().extract_features(uuid4())
        assert "nearest_site_m" in features

    def test_generate_hypotheses(self):
        hypos = ArchaeologicalPerspective().generate_hypotheses(uuid4())
        assert len(hypos) == len(_ARCHAEOLOGICAL_ELEMENTS)

    def test_archaeological_elements(self):
        assert "horg" in _ARCHAEOLOGICAL_ELEMENTS
        assert "haug" in _ARCHAEOLOGICAL_ELEMENTS
        assert "ting" in _ARCHAEOLOGICAL_ELEMENTS


# --- Religious Perspective ---


class TestReligiousPerspective:
    """Tests for ReligiousPerspective."""

    def test_metadata(self):
        p = ReligiousPerspective()
        assert p.perspective_id == "religious"

    def test_is_base_perspective(self):
        assert isinstance(ReligiousPerspective(), BasePerspective)

    def test_extract_features(self):
        features = ReligiousPerspective().extract_features(uuid4())
        assert "deity_element" in features
        assert "cult_element" in features

    def test_generate_hypotheses(self):
        hypos = ReligiousPerspective().generate_hypotheses(uuid4())
        assert len(hypos) == len(_DEITY_ELEMENTS) + len(_CULT_ELEMENTS)

    def test_deity_elements(self):
        assert "tor" in _DEITY_ELEMENTS
        assert "odin" in _DEITY_ELEMENTS
        assert "frøy" in _DEITY_ELEMENTS

    def test_cult_elements(self):
        assert "hov" in _CULT_ELEMENTS
        assert "horg" in _CULT_ELEMENTS
        assert "ve" in _CULT_ELEMENTS


# --- Astronomical Perspective ---


class TestAstronomicalPerspective:
    """Tests for AstronomicalPerspective."""

    def test_metadata(self):
        p = AstronomicalPerspective()
        assert p.perspective_id == "astronomical"

    def test_is_base_perspective(self):
        assert isinstance(AstronomicalPerspective(), BasePerspective)

    def test_extract_features(self):
        features = AstronomicalPerspective().extract_features(uuid4())
        assert "aspect_deg" in features

    def test_generate_hypotheses(self):
        hypos = AstronomicalPerspective().generate_hypotheses(uuid4())
        assert len(hypos) > 0
        # Should have directional + solstice hypotheses
        assert any("solstice" in h.claim.lower() for h in hypos)

    def test_solar_azimuth_calculation(self):
        # Summer solstice at 60°N (declination ~23.44°)
        az = AstronomicalPerspective.solar_azimuth_at_latitude(60.0, 23.44)
        assert 30 < az < 50  # Should be roughly 37°

    def test_astronomical_elements(self):
        assert "sol" in _ASTRONOMICAL_ELEMENTS
        assert "nord" in _ASTRONOMICAL_ELEMENTS


# --- Colour Perspective ---


class TestColourPerspective:
    """Tests for ColourPerspective."""

    def test_metadata(self):
        p = ColourPerspective()
        assert p.perspective_id == "colour"

    def test_is_base_perspective(self):
        assert isinstance(ColourPerspective(), BasePerspective)

    def test_extract_features(self):
        features = ColourPerspective().extract_features(uuid4())
        assert "dominant_colour_rgb" in features
        assert "ndvi" in features

    def test_generate_hypotheses(self):
        hypos = ColourPerspective().generate_hypotheses(uuid4())
        assert len(hypos) == len(_COLOUR_ELEMENTS)

    def test_colour_elements(self):
        assert "svart" in _COLOUR_ELEMENTS
        assert "hvit" in _COLOUR_ELEMENTS
        assert "grønn" in _COLOUR_ELEMENTS
        assert "blå" in _COLOUR_ELEMENTS


# --- Acoustic Perspective ---


class TestAcousticPerspective:
    """Tests for AcousticPerspective."""

    def test_metadata(self):
        p = AcousticPerspective()
        assert p.perspective_id == "acoustic"

    def test_is_base_perspective(self):
        assert isinstance(AcousticPerspective(), BasePerspective)

    def test_extract_features(self):
        features = AcousticPerspective().extract_features(uuid4())
        assert "terrain_concavity" in features
        assert "wind_exposure" in features

    def test_generate_hypotheses(self):
        hypos = AcousticPerspective().generate_hypotheses(uuid4())
        assert len(hypos) == len(_ACOUSTIC_ELEMENTS)

    def test_acoustic_elements(self):
        assert "ljom" in _ACOUSTIC_ELEMENTS
        assert "dur" in _ACOUSTIC_ELEMENTS
        assert "stil" in _ACOUSTIC_ELEMENTS


# --- Mortality Perspective ---


class TestMortalityPerspective:
    """Tests for MortalityPerspective."""

    def test_metadata(self):
        p = MortalityPerspective()
        assert p.perspective_id == "mortality"

    def test_is_base_perspective(self):
        assert isinstance(MortalityPerspective(), BasePerspective)

    def test_extract_features(self):
        features = MortalityPerspective().extract_features(uuid4())
        assert "in_flood_zone" in features
        assert "in_avalanche_zone" in features

    def test_generate_hypotheses(self):
        hypos = MortalityPerspective().generate_hypotheses(uuid4())
        assert len(hypos) == len(_HAZARD_ELEMENTS)

    def test_hazard_elements(self):
        assert "ras" in _HAZARD_ELEMENTS
        assert "skred" in _HAZARD_ELEMENTS
        assert "flom" in _HAZARD_ELEMENTS


# --- Migration Perspective ---


class TestMigrationPerspective:
    """Tests for MigrationPerspective."""

    def test_metadata(self):
        p = MigrationPerspective()
        assert p.perspective_id == "migration"

    def test_is_base_perspective(self):
        assert isinstance(MigrationPerspective(), BasePerspective)

    def test_extract_features(self):
        features = MigrationPerspective().extract_features(uuid4())
        assert "name_cluster_id" in features
        assert "distance_to_origin_km" in features

    def test_generate_hypotheses(self):
        hypos = MigrationPerspective().generate_hypotheses(uuid4())
        assert len(hypos) > len(_MIGRATION_ELEMENTS)  # elements + migrations

    def test_migration_elements(self):
        assert "ny" in _MIGRATION_ELEMENTS
        assert "gamla" in _MIGRATION_ELEMENTS


# --- Economic Perspective ---


class TestEconomicPerspective:
    """Tests for EconomicPerspective."""

    def test_metadata(self):
        p = EconomicPerspective()
        assert p.perspective_id == "economic"

    def test_is_base_perspective(self):
        assert isinstance(EconomicPerspective(), BasePerspective)

    def test_extract_features(self):
        features = EconomicPerspective().extract_features(uuid4())
        assert "on_trade_route" in features
        assert "centrality_index" in features

    def test_generate_hypotheses(self):
        hypos = EconomicPerspective().generate_hypotheses(uuid4())
        # elements + 1 network centrality hypothesis
        assert len(hypos) == len(_ECONOMIC_ELEMENTS) + 1

    def test_economic_elements(self):
        assert "kaup" in _ECONOMIC_ELEMENTS
        assert "hamn" in _ECONOMIC_ELEMENTS
        assert "torg" in _ECONOMIC_ELEMENTS


# --- Historical Perspective (Milestone 12.1) ---


class TestHistoricalPerspective:
    """Tests for HistoricalPerspective."""

    def test_metadata(self):
        p = HistoricalPerspective()
        assert p.perspective_id == "historical"
        assert p.name == "Historical/Diachronic"

    def test_is_base_perspective(self):
        assert isinstance(HistoricalPerspective(), BasePerspective)

    def test_extract_features(self):
        features = HistoricalPerspective().extract_features(uuid4())
        assert "assigned_period" in features
        assert "earliest_attestation_year" in features
        assert "settlement_wave" in features

    def test_generate_hypotheses(self):
        hypos = HistoricalPerspective().generate_hypotheses(uuid4())
        assert len(hypos) == len(_PERIOD_ELEMENTS)
        assert all(isinstance(h, Hypothesis) for h in hypos)

    def test_period_elements_defined(self):
        assert "heim" in _PERIOD_ELEMENTS
        assert "by" in _PERIOD_ELEMENTS
        assert "rud" in _PERIOD_ELEMENTS
        assert "torp" in _PERIOD_ELEMENTS
        assert "ødegård" in _PERIOD_ELEMENTS

    def test_assign_period_viking_age(self):
        p = HistoricalPerspective()
        period, confidence = p.assign_period(["by"])
        assert period == "viking_age"
        assert confidence > 0.0

    def test_assign_period_medieval_clearing(self):
        p = HistoricalPerspective()
        period, confidence = p.assign_period(["rud"])
        assert period == "high_medieval"
        assert confidence > 0.0

    def test_assign_period_unknown(self):
        p = HistoricalPerspective()
        period, confidence = p.assign_period(["xyz"])
        assert period is None
        assert confidence == 0.0

    def test_assign_period_mixed(self):
        p = HistoricalPerspective()
        period, confidence = p.assign_period(["heim", "by"])
        # Should pick one based on weighting
        assert period in ("iron_age", "viking_age")
        assert 0.0 < confidence <= 1.0


# --- Ecological Perspective (Milestone 12.2) ---


class TestEcologicalPerspective:
    """Tests for EcologicalPerspective."""

    def test_metadata(self):
        p = EcologicalPerspective()
        assert p.perspective_id == "ecological"
        assert p.name == "Ecological/Biological"

    def test_is_base_perspective(self):
        assert isinstance(EcologicalPerspective(), BasePerspective)

    def test_extract_features(self):
        features = EcologicalPerspective().extract_features(uuid4())
        assert "flora_element" in features
        assert "fauna_element" in features
        assert "vegetation_zone" in features

    def test_generate_hypotheses(self):
        hypos = EcologicalPerspective().generate_hypotheses(uuid4())
        assert len(hypos) == len(_FLORA_ELEMENTS) + len(_FAUNA_ELEMENTS)
        assert all(isinstance(h, Hypothesis) for h in hypos)

    def test_flora_elements_defined(self):
        assert "bjørk" in _FLORA_ELEMENTS
        assert "eik" in _FLORA_ELEMENTS
        assert "gran" in _FLORA_ELEMENTS
        assert "furu" in _FLORA_ELEMENTS

    def test_fauna_elements_defined(self):
        assert "ulv" in _FAUNA_ELEMENTS
        assert "bjørn" in _FAUNA_ELEMENTS
        assert "ørn" in _FAUNA_ELEMENTS
        assert "laks" in _FAUNA_ELEMENTS

    def test_classify_flora(self):
        p = EcologicalPerspective()
        result = p.classify_element("bjørk")
        assert result is not None
        assert result["category"] == "flora"
        assert result["species"] == "Betula"

    def test_classify_fauna(self):
        p = EcologicalPerspective()
        result = p.classify_element("ulv")
        assert result is not None
        assert result["category"] == "fauna"
        assert result["species"] == "Canis lupus"

    def test_classify_unknown(self):
        p = EcologicalPerspective()
        assert p.classify_element("xyz") is None


# --- Legal Perspective (Milestone 12.3) ---


class TestLegalPerspective:
    """Tests for LegalPerspective."""

    def test_metadata(self):
        p = LegalPerspective()
        assert p.perspective_id == "legal"
        assert p.name == "Legal/Administrative"

    def test_is_base_perspective(self):
        assert isinstance(LegalPerspective(), BasePerspective)

    def test_extract_features(self):
        features = LegalPerspective().extract_features(uuid4())
        assert "legal_element" in features
        assert "nearest_boundary_m" in features
        assert "centrality_score" in features

    def test_generate_hypotheses(self):
        hypos = LegalPerspective().generate_hypotheses(uuid4())
        assert len(hypos) == len(_LEGAL_ELEMENTS)
        assert all(isinstance(h, Hypothesis) for h in hypos)

    def test_legal_elements_defined(self):
        assert "ting" in _LEGAL_ELEMENTS
        assert "herad" in _LEGAL_ELEMENTS
        assert "grense" in _LEGAL_ELEMENTS
        assert "galge" in _LEGAL_ELEMENTS

    def test_classify_assembly_element(self):
        p = LegalPerspective()
        result = p.classify_element("ting")
        assert result is not None
        assert result["type"] == "assembly"

    def test_classify_boundary_element(self):
        p = LegalPerspective()
        result = p.classify_element("grense")
        assert result is not None
        assert result["type"] == "boundary"

    def test_classify_unknown(self):
        p = LegalPerspective()
        assert p.classify_element("xyz") is None


# --- Temporal Perspective (Milestone 12.4) ---


class TestTemporalPerspective:
    """Tests for TemporalPerspective."""

    def test_metadata(self):
        p = TemporalPerspective()
        assert p.perspective_id == "temporal"
        assert p.name == "Temporal Cycles & Calendar"

    def test_is_base_perspective(self):
        assert isinstance(TemporalPerspective(), BasePerspective)

    def test_extract_features(self):
        features = TemporalPerspective().extract_features(uuid4())
        assert "temporal_element" in features
        assert "season" in features
        assert "growing_season_days" in features

    def test_generate_hypotheses(self):
        hypos = TemporalPerspective().generate_hypotheses(uuid4())
        assert len(hypos) == len(_TEMPORAL_ELEMENTS)
        assert all(isinstance(h, Hypothesis) for h in hypos)

    def test_temporal_elements_defined(self):
        assert "vår" in _TEMPORAL_ELEMENTS
        assert "seter" in _TEMPORAL_ELEMENTS
        assert "jul" in _TEMPORAL_ELEMENTS
        assert "slått" in _TEMPORAL_ELEMENTS

    def test_classify_seasonal(self):
        p = TemporalPerspective()
        result = p.classify_element("vår")
        assert result is not None
        assert result["type"] == "seasonal"
        assert result["season"] == "spring"

    def test_classify_transhumance(self):
        p = TemporalPerspective()
        result = p.classify_element("seter")
        assert result is not None
        assert result["type"] == "transhumance"

    def test_classify_unknown(self):
        p = TemporalPerspective()
        assert p.classify_element("xyz") is None


# --- Medicinal Perspective (Milestone 12.5) ---


class TestMedicinalPerspective:
    """Tests for MedicinalPerspective."""

    def test_metadata(self):
        p = MedicinalPerspective()
        assert p.perspective_id == "medicinal"
        assert p.name == "Medicinal & Healing Landscape"

    def test_is_base_perspective(self):
        assert isinstance(MedicinalPerspective(), BasePerspective)

    def test_extract_features(self):
        features = MedicinalPerspective().extract_features(uuid4())
        assert "healing_element" in features
        assert "nearest_thermal_spring_m" in features
        assert "water_temperature_c" in features

    def test_generate_hypotheses(self):
        p = MedicinalPerspective()
        hypos = p.generate_hypotheses(uuid4())
        expected = (
            len(_HEALING_WATER_ELEMENTS) + len(_CARE_ELEMENTS) + len(_MEDICINAL_PLANT_ELEMENTS)
        )
        assert len(hypos) == expected
        assert all(isinstance(h, Hypothesis) for h in hypos)

    def test_generate_hypotheses_no_plants(self):
        p = MedicinalPerspective(include_plants=False)
        hypos = p.generate_hypotheses(uuid4())
        expected = len(_HEALING_WATER_ELEMENTS) + len(_CARE_ELEMENTS)
        assert len(hypos) == expected

    def test_healing_water_elements(self):
        assert "bad" in _HEALING_WATER_ELEMENTS
        assert "spa" in _HEALING_WATER_ELEMENTS
        assert "varm" in _HEALING_WATER_ELEMENTS
        assert "kilde" in _HEALING_WATER_ELEMENTS

    def test_care_elements(self):
        assert "hospital" in _CARE_ELEMENTS
        assert "spital" in _CARE_ELEMENTS
        assert "lazarett" in _CARE_ELEMENTS

    def test_medicinal_plant_elements(self):
        assert "lind" in _MEDICINAL_PLANT_ELEMENTS
        assert "selje" in _MEDICINAL_PLANT_ELEMENTS

    def test_classify_healing_water(self):
        p = MedicinalPerspective()
        result = p.classify_element("bad")
        assert result is not None
        assert result["category"] == "healing_water"
        assert result["type"] == "thermal"

    def test_classify_care(self):
        p = MedicinalPerspective()
        result = p.classify_element("hospital")
        assert result is not None
        assert result["category"] == "care_facility"

    def test_classify_plant(self):
        p = MedicinalPerspective()
        result = p.classify_element("selje")
        assert result is not None
        assert result["category"] == "medicinal_plant"
        assert result["species"] == "Salix"

    def test_classify_unknown(self):
        p = MedicinalPerspective()
        assert p.classify_element("xyz") is None
