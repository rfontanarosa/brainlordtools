# brainlordtools

A set of ROM-hacking utilities for old school videogames - text dumping, reinsertion, compression, and graphics tools.

## Compatible games

| ID         | Game                                       | Platform | Status      | Dependency                     |
| ---------- | ------------------------------------------ | -------- | ----------- | ------------------------------ |
| 7thsaga    | 7th Saga, The                              | SNES     | Stable      |                                |

## Getting started

`_create_db.sh` is the first script to run before starting work on a project.
It creates the SQLite database for a game from the schema; the import/export
scripts all depend on this database existing.

```sh
./_create_db.sh <game_id>
```

For example, `./_create_db.sh som`. Once the database exists, you can import the
English dump (`_import_dump.sh`), then export/import translations
(`_export_translation.sh` / `_import_translation.sh`).
