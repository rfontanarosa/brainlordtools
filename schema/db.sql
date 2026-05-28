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

CREATE TABLE IF NOT EXISTS translations_history (
    id_text INTEGER NOT NULL,
    project TEXT NOT NULL,
    author TEXT NOT NULL,
    translation TEXT,
    status INTEGER,
    date INTEGER,
    tags TEXT,
    comment TEXT,
    operation TEXT NOT NULL,
    changed_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

-- Archive the previous record whenever an existing translation is edited.
-- The guard skips no-op updates (e.g. re-saving identical content).
CREATE TRIGGER IF NOT EXISTS translations_history_au
AFTER UPDATE ON translations
WHEN OLD.translation IS NOT NEW.translation
   OR OLD.status IS NOT NEW.status
   OR OLD.tags IS NOT NEW.tags
   OR OLD.comment IS NOT NEW.comment
BEGIN
    INSERT INTO translations_history (id_text, project, author, translation, status, date, tags, comment, operation)
    VALUES (OLD.id_text, OLD.project, OLD.author, OLD.translation, OLD.status, OLD.date, OLD.tags, OLD.comment, 'UPDATE');
END;

-- Archive the record whenever a translation is deleted.
CREATE TRIGGER IF NOT EXISTS translations_history_ad
AFTER DELETE ON translations
BEGIN
    INSERT INTO translations_history (id_text, project, author, translation, status, date, tags, comment, operation)
    VALUES (OLD.id_text, OLD.project, OLD.author, OLD.translation, OLD.status, OLD.date, OLD.tags, OLD.comment, 'DELETE');
END;
