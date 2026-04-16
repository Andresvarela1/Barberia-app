CREATE TABLE IF NOT EXISTS barberias (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    usuario TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    rol TEXT NOT NULL,
    telefono TEXT,
    cortes_acumulados INTEGER NOT NULL DEFAULT 0,
    barberia_id INTEGER NOT NULL,
    CONSTRAINT fk_usuarios_barberia
        FOREIGN KEY (barberia_id)
        REFERENCES barberias(id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS reservas (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    barbero TEXT NOT NULL,
    servicio TEXT NOT NULL,
    precio INTEGER NOT NULL,
    inicio TIMESTAMP NOT NULL,
    fin TIMESTAMP NOT NULL,
    barberia_id INTEGER NOT NULL,
    CONSTRAINT fk_reservas_barberia
        FOREIGN KEY (barberia_id)
        REFERENCES barberias(id)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_reservas_barberia ON reservas(barberia_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_barberia ON usuarios(barberia_id);

CREATE EXTENSION IF NOT EXISTS btree_gist;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'reservas_no_solapadas'
    ) THEN
        ALTER TABLE reservas
        ADD CONSTRAINT reservas_no_solapadas
        EXCLUDE USING gist (
            barberia_id WITH =,
            barbero WITH =,
            tsrange(inicio, fin, '[)') WITH &&
        );
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'No se pudo crear reservas_no_solapadas: %', SQLERRM;
END $$;
