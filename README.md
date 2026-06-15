# brainlordtools

A set of ROM-hacking utilities for old school videogames - text dumping, reinsertion, compression, and graphics tools.

## Compatible games

| ID         | Game                                       | Platform | Status      | Dependency                     |
| ---------- | ------------------------------------------ | -------- | ----------- | ------------------------------ |
| 7thsaga    | 7th Saga, The                              | SNES     | Stable      |                                |
| alcahest   | Alcahest                                   | SNES     | Stable      | alcahest-tool                  |
| brainlord  | Brain Lord                                 | SNES     | Stable      |                                |
| brandishdr | Brandish: The Dark Revenant                | PSP      | In progress | brandish-dr-tool               |
| bof2       | Breath of Fire 2                           | SNES     | In progress |                                |
| equinox    | Equinox                                    | SNES     | Stable      |                                |
| ffmq       | Final Fantasy: Mystic Quest                | SNES     | Stable      | Final-Fantasy-Mystic-Quest-ITA |
| gargoyle   | Gargoyle's Quest                           | GB       | Stable      |                                |
| ignition   | Ignition Factor, The                       | SNES     | Stable      |                                |
| lom        | Legend of Mana                             | PSX      | In progress | Legend-Of-Mana-ITA             |
| lufia      | Lufia & the Fortress of Doom               | SNES     | Stable      |                                |
| neugier    | Neugier: Umi to Kaze no Koudou             | SNES     | Stable      |                                |
| ruinarm    | Ruin Arm                                   | SNES     | In progress | Romhacking                     |
| soe        | Secret of Evermore                         | SNES     | Stable      | Romhacking                     |
| som        | Secret of Mana                             | SNES     | Stable      |                                |
| som_pal    | Secret of Mana (PAL)                       | SNES     | Stable      |                                |
| smrpg      | Super Mario RPG: Legend of the Seven Stars | SNES     | Stable      | Super-Mario-RPG-ITA            |
| starocean  | Star Ocean                                 | SNES     | Stable      | PrivateRomhacking              |
| spike      | Twisted Tales of Spike McFang, The         | SNES     | Stable      | mcfang-dec                     |

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
