schema = """
CREATE TABLE owners (
    name TEXT PRIMARY KEY,
    key TEXT
);

CREATE TABLE zones (
    id TEXT PRIMARY KEY,
    owner TEXT,
    aws_access_key TEXT,
    aws_secret_key TEXT,
    name TEXT
);

CREATE TABLE domains (
    zone_id TEXT,
    name TEXT,
    type TEXT,
    value TEXT,
    PRIMARY KEY (zone_id, name)
);
"""
