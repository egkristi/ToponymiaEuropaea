"""Configuration management using pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or config file."""

    model_config = SettingsConfigDict(
        env_prefix="TOPONYMIA_",
        env_file=".env",
    )

    # Database
    database_url: str = "postgresql://localhost:5432/toponymia"

    # Paths
    data_dir: Path = Path("data")
    cache_dir: Path = Path(".cache")

    # GeoNames
    geonames_username: str = ""
    geonames_dump_url: str = "https://download.geonames.org/export/dump"

    # Wikidata
    wikidata_endpoint: str = "https://query.wikidata.org/sparql"

    # Analysis defaults
    default_srid: int = 4326
    default_n_permutations: int = 10000
    significance_level: float = 0.05

    # Ontology
    ontology_version: str = "1.0.0"

    # API
    api_host: str = "0.0.0.0"  # noqa: S104
    api_port: int = 8000


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
