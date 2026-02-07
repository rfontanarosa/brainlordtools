CREATE TABLE IF NOT EXISTS texts (
    id INTEGER PRIMARY KEY,
    text BLOB NOT NULL,
    text_decoded TEXT NOT NULL,
    address TEXT NOT NULL,
    pointer_addresses TEXT,
    size INTEGER,
    block TEXT,
    ref TEXT
);

CREATE TABLE IF NOT EXISTS translations (
    id_text INTEGER NOT NULL,
    project TEXT NOT NULL,
    author TEXT NOT NULL,
    translation TEXT NOT NULL,
    status INTEGER NOT NULL,
    date INTEGER NOT NULL,
    tags TEXT,
    comment TEXT,
    PRIMARY KEY(id_text, project, author)
);
