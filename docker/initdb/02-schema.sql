-- Create core tables for Toponymia Europaea operational store
-- Applied after extensions (01-extensions.sql)

CREATE TABLE IF NOT EXISTS places (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    normalized_name TEXT,
    country_code CHAR(2) NOT NULL,
    source TEXT NOT NULL,
    source_id TEXT,
    coordinates GEOMETRY(Point, 4326),
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    phonetic_key TEXT,
    h3_index TEXT,
    language_code TEXT,
    feature_class TEXT,
    feature_code TEXT,
    admin1 TEXT,
    admin2 TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_places_country ON places(country_code);
CREATE INDEX IF NOT EXISTS idx_places_source ON places(source);
CREATE INDEX IF NOT EXISTS idx_places_name_trgm ON places USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_places_normalized ON places USING gin(normalized_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_places_phonetic ON places(phonetic_key);
CREATE INDEX IF NOT EXISTS idx_places_h3 ON places(h3_index);
CREATE INDEX IF NOT EXISTS idx_places_coordinates ON places USING gist(coordinates);

-- Attestations table for historical name forms
CREATE TABLE IF NOT EXISTS attestations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    place_id UUID REFERENCES places(id) ON DELETE CASCADE,
    name_form TEXT NOT NULL,
    year_from INTEGER,
    year_to INTEGER,
    source_document TEXT,
    language_code TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_attestations_place ON attestations(place_id);
CREATE INDEX IF NOT EXISTS idx_attestations_year ON attestations(year_from, year_to);
