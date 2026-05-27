CREATE TABLE IF NOT EXISTS texts (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    address TEXT NOT NULL,
    pointer_addresses TEXT,
    size INTEGER,
    block TEXT,
    ref TEXT,
    dump_type TEXT,
    filename TEXT,
    file_index INTEGER
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
