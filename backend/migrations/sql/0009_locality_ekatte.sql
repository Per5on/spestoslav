CREATE TABLE IF NOT EXISTS locality_ekatte (
    locality_id UUID PRIMARY KEY REFERENCES inhabited_localities(id),
    ekatte_code VARCHAR(5) NOT NULL,
    source_reference VARCHAR(500) NOT NULL,
    source_as_of DATE NOT NULL,
    CONSTRAINT uq_locality_ekatte_code UNIQUE (ekatte_code),
    CONSTRAINT ck_locality_ekatte_length CHECK (length(ekatte_code) = 5)
);
