CREATE TABLE barberias (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL
);

CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    usuario TEXT NOT NULL,
    password TEXT NOT NULL,
    rol TEXT NOT NULL,
    telefono TEXT,
    barberia_id INTEGER NOT NULL,
    CONSTRAINT fk_usuarios_barberia
        FOREIGN KEY (barberia_id)
        REFERENCES barberias(id)
        ON DELETE RESTRICT
);

CREATE TABLE reservas (
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
