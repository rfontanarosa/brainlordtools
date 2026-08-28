# Secret of Mana (`som`)

How to dump, translate and rebuild **Secret of Mana (USA)** with `bin/som.sh`,
`brainlordtools/som.py` and the ASM patches.

---

## 1. The two folders

The work is split in two repositories:

| Folder | What it contains |
| --- | --- |
| `brainlordtools/` (this repo) | The code: `bin/som.sh`, `brainlordtools/som.py`, `brainlordtools/_som/`, `manager.py` |
| `../brainlordresources/som/` | The data: ROM, tables, dumps, translations, graphics, ASM patches, database |

`bin/som.sh` is only the "recipe": it calls the Python tools and `asar` in the
right order, always reading and writing inside `../brainlordresources/som/`.

### Files inside `../brainlordresources/som/`

| Folder | Content |
| --- | --- |
| `roms/` | `Secret of Mana (USA).sfc` (input) and `Secret of Mana (ITA).sfc` (output) |
| `db/som.sqlite3` | The database with the English text and every translation |
| `tables/` | `.tbl` files: byte ↔ character conversion |
| `dump_text/` | English text dumped from the ROM (**overwritten at every run**) |
| `dump_misc/` | DTE table, decompressed intro/title data, tilemaps (**overwritten at every run**) |
| `dump_gfx/` | Menu icons extracted from the ROM |
| `translated_text/` | Translated text files exported from the database |
| `translated_misc/` | The files you actually edit and re-insert (DTE, intro, tilemaps) |
| `translated_gfx/` | Translated menu icons |
| `asm/` | The ASM patches (`font.asm`, `menus.asm`, `intro.asm`, …) |
| `tilesets/` | `intro_tileset.png`, `the_end_tileset.png` — reference images for the tilemaps |

---

## 2. Before you start

1. Put the original ROM in `roms/Secret of Mana (USA).sfc`.
   The script checks its CRC and stops if it is the wrong ROM.
2. Install the Python requirements: `pip install -r requirements.txt`.
3. Install **asar** (the SNES assembler) and make sure `asar` works in the terminal.
4. Create the database once:

   ```sh
   ./_create_db.sh som
   ```

---

## 3. The normal work cycle

```sh
cd bin && ./som.sh          # 1. dump (and build the ROM with what is in the DB)
cd .. && ./_import_dump.sh som               # 2. English text -> database
./_export_translation.sh som clomax          # 3. database -> translated_text_clomax/
#    ... translate the .txt files ...
./_import_translation.sh som clomax          # 4. translated .txt -> database
cd bin && ./som.sh          # 5. rebuild -> roms/Secret of Mana (ITA).sfc
```

Export and import use the same folder and the same two file names:
`translated_text_<user>/dump_events_eng.txt` and `dump_texts_eng.txt`. The
`_eng` in the name comes from the dump the entries belong to, not from the
language of the text: those files hold your translation.

The name you pass to `_import_translation.sh` is the author your work is saved
under, and it must be the same as `USER=` at the top of `bin/som.sh`: that is
the author `insert_text` reads back.

Points 2 and 3 are needed only the first time (or when the dump changes).
`dump_text` already writes the English text into the database by itself, so
`_import_dump.sh` is really a way to reload it from the `.txt` files.
Day by day you only do: **translate → import translation → run `som.sh`**.

Two things to remember:

* `som.sh` **always dumps first and inserts after**, in the same run. The dump
  reads the English ROM, the insert reads the **database**, not the `.txt`
  files. If you edit a `.txt` file you must re-import it, otherwise nothing changes.
* The dump erases and recreates `dump_text/` and `dump_misc/`. Never keep your
  own work there: your files go in `translated_text/`, `translated_misc/`,
  `translated_gfx/`.

---

## 4. What `som.sh` does, step by step

1. **Checks** the source ROM CRC and copies it to `Secret of Mana (ITA).sfc`.
   Everything after this works on the copy.
2. **`som.py dump_text`** – dumps all the dialogue and menu text to
   `dump_text/` and to the database.
3. **`som.py dump_misc`** – dumps the DTE table to `dump_misc/dte.csv`.
4. **`_som/decomp.py`** – decompresses the intro code, the intro data and the
   title screen to `dump_misc/*.bin`.
5. **`som.py dump_tilemap`** – takes the intro tilemap and the "THE END" screen
   out of the decompressed intro data.
6. **`_som/som_icons.py extract`** – extracts the 10 menu icons that contain
   text (EQUIP, HP, MP, STAT, LEVEL, …) to `dump_gfx/`.
7. **`asar asm/intro_ram.asm`** – patches `translated_misc/intro-code.bin`
   (the intro routine that runs from RAM).
8. **`som.py insert_tilemap`** – puts your translated tilemaps back into
   `translated_misc/intro-data.bin`.
9. **`_som/decomp.py --compress`** – recompresses intro code and intro data.
10. **`som.py insert_text`** – writes the translated text into the ROM and
    recalculates all the pointers.
11. **`som.py insert_misc`** – writes the DTE table, the compass letters and the
    compressed intro into the ROM.
12. **`_som/som_icons.py insert`** – puts the translated icons back.
13. **`asar`** on `font.asm`, `menus.asm`, `intro.asm` – the code patches
    (new font, translated menus, translated intro text).

---

## 5. `som.py` commands

| Command | What it does |
| --- | --- |
| `dump_text` | Reads every text block, decodes it with the `.tbl` table and writes `dump_text/dump_events_eng.txt`, `dump_text/dump_texts_eng.txt` and the `texts` table of the database |
| `insert_text` | Takes the translations of the `-u` author from the database, encodes them and writes them in the ROM, then rewrites every pointer |
| `dump_misc` | Dumps the DTE table (the 2-letter shortcuts) to `dump_misc/dte.csv` |
| `insert_misc` | Writes back: DTE table, `7FB00_cardinals.bin` (compass letters), compressed intro code and data |
| `dump_tilemap` | From the decompressed `intro-data.bin`, extracts `intro-tilemap.bin`, `the-end-gfx.bin`, `the-end-tilemap.bin` |
| `insert_tilemap` | Puts those three files back inside `intro-data.bin` |

Each line of the dump looks like this:

```
[ID=2258 BLOCK=2 EVENT=0x8d1 START=0xaa1da POINTERS=0xa09a2]
Mushboom[END]
```

Only the line **below** the `[ID=...]` header is text to translate. Never touch
the header, and never remove `[END]` or the tags in square brackets: they are
game commands (line breaks, colours, pauses, character names…).

**The credits (ID 1278)** are a special case: everything between
`[SWAP_TABLE_START]` and `[SWAP_TABLE_END]` uses a second character set
(`som_credits.tbl`, capital letters only). Keep those two tags where they are.

---

## 6. The text blocks

`dump_text` splits the text into 8 blocks. This table tells you where each
thing lives and how much room it has.

| Block | ID range | Content | Written to | Space |
| --- | --- | --- | --- | --- |
| 1 | 1 – 1024 | Events / dialogue (first half) | in place, `0x90800`–`0x9F2D6` | ~60 KB |
| 2 | 1025 – 2561 | Events / dialogue (second half), item, spell and **monster names** (ID 2256–2383) | in place, `0xA0C02`–`0xAB573` | ~43 KB |
| 3 | 2562 – 2577 | Status names (POISONED, TRANSFORMED, …) | moved to `0x74900`–`0x74FFF` | shared |
| 4 | 2578 – 2605 | File select, name entry, controller/window edit, skill screens | moved to `0x74900`–`0x74FFF` | shared |
| 5 | 2606 – 2614 | Long tutorial messages | moved to `0xB3800`–`0xB3FFF` | 2 KB |
| 6 | 2615 – 2622 | Weapon names (GLOVES, SWORD, …) | moved to `0x74900`–`0x74FFF` | shared |
| 7 | 2623 – 2728 | Battle messages ("… is unconscious!") | in place, `0x5E6B`–`0x637D` | ~1.3 KB |
| 8 | 2729 – 2737 | Blacksmith / shop messages | in place, `0x19FE20`–`0x19FEF4` | 212 bytes |

Blocks 3, 4 and 6 share the same free area (`0x74900`–`0x74FFF`, 1792 bytes).
Roughly two thirds of block 4 is **skipped** by the inserter, and on purpose:
those entries are not text. Each menu screen has one real string followed by one
or two entries holding its layout (length, tile, position bytes), which decode
as control-code garbage like `[TOGGLE_INVISIBILITY_A]{e8}[END]`. They must stay
at their original address, so they are never moved or repointed — and some of
them are patched by `menus.asm` instead (ID 2600 is `0x7754A`, patched at
`$C7754B`; ID 2603 is `0x77558`, patched at `$C77559`). If you translate one of
those lines nothing happens: they are simply skipped.

If a block does not fit, the tool stops with:

```
ERROR: BLOCK OVERFLOW at ID 1234!
```

and tells you how many bytes you went over. Shorten the text, or use more DTE.

---

## 7. The `.tbl` tables

| File | Used for |
| --- | --- |
| `som_main.tbl` | Dumping the English ROM |
| `som_main_with_dte.tbl` | English + original DTE pairs |
| `som_main_with_dte_ita.tbl` | **Inserting the Italian text** (accents + Italian DTE) |
| `som_main_ita.tbl` | Inserting the misc texts (DTE table) |
| `som_credits.tbl` | The credits, which use a different character set |
| `som_main_with_dte_sadnes.tbl` | Only to re-read the old SADNES translation |

The Italian tables add 7 characters that do not exist in the American ROM:

| Byte | Char |
| --- | --- |
| `D3` `D4` `D5` `D6` `D7` `D8` `D9` | `à` `è` `é` `ì` `ò` `ù` `È` |

Those 7 slots come from the `font.asm` patch (see below). If you add a new
character you must draw it in `font.bin` **and** add the line in the `.tbl`.

---

## 8. DTE (two letters in one byte)

DTE is how the text is compressed: one byte prints two characters. It is the
main tool to make a long translation fit.

* Dumped to `dump_misc/dte.csv`: 61 pairs, columns `text_address,text,trans`.
  Write your pair in the `trans` column; if `trans` is empty, `text` is used.
* You edit `translated_misc/dte.csv` and `insert_misc` writes it at `0x74350`.
* There is room for **69 pairs** (138 bytes). Over that, the tool stops with
  `Text size exceeds!`.
* Row order matters, it is what maps a pair to a byte:

| CSV rows | Byte codes |
| --- | --- |
| 1 – 29 | `$60` – `$7C` |
| 30 – 31 | not used (leave as they are) |
| 32 – 61 | `$DA` – `$F7` |

**Every pair you change in `dte.csv` must be changed in
`som_main_with_dte_ita.tbl` too, on the same byte code.** If the two do not
match, the text will be inserted correctly but shown as nonsense.

To find the best pairs for an Italian script you can use `mte_optimizer.py`
(there is a ready-made command, commented out, at the end of `som.sh`).

---

## 9. The other Python tools

### `_som/decomp.py` — compression

The intro and the title screen are stored compressed.

```sh
# decompress: take 0x77C00 out of the ROM
python _som/decomp.py "rom.sfc" "intro-code.bin" --base-offset="77C00"

# recompress
python _som/decomp.py "intro-code.bin" "intro-code-compressed.bin" --compress --compression-key="1"
```

The `--compression-key` must stay the same as the original block
(1 = intro code, 4 = intro data, 3 = title screen), and the compressed file
must not be bigger than the original space:

| Block | Address | Max size |
| --- | --- | --- |
| intro code | `0x77C00` | 14437 bytes |
| intro data | `0x7B480` | 3390 bytes |
| title screen | `0x1CE800` | 2096 bytes (currently disabled in `som.sh`) |

### `_som/som_icons.py` — menu icons

The icons with text inside (EQUIP, HP, MP, STAT, LEVEL, ACT., CONTROLLER EDIT,
WIN EDIT) are stored in a packed 3bpp format at `0x128400`.

```sh
python _som/som_icons.py extract "rom.sfc" "menu_icon_equip.bin" --sprite 9
python _som/som_icons.py insert  "menu_icon_equip.bin" "rom.sfc" --sprite 9
```

`extract` gives you a normal 16×16 tile file you can open in a tile editor
(YY-CHR, Tilemolester); `insert` packs it back. Sprite numbers used by `som.sh`:
9 (EQUIP), 16/17 (HP), 62/63 (MP), 170 (STAT), 171 (LEVEL), 172 (ACT.),
173 (CONTROLLER EDIT), 174 (WIN EDIT). Edit the files in `translated_gfx/`.

---

## 10. The ASM patches (`../brainlordresources/som/asm/`)

These are assembled with **asar**. They change the game code, so they can do
things the text tools cannot: bigger font, longer menu strings, a rewritten
intro.

### `font.asm` — font and DTE
Applied to the ROM. It:
* moves the font to free space (`$C74400`) and loads it from `font.bin`;
* moves the DTE table to `$C74350` (69 pairs instead of the original ones);
* raises the character limit so 7 more characters exist (`$D3`–`$D9`, the accents);
* clears the original font and DTE data.

**To change the font**: edit `asm/font.bin` with a tile editor and run the
script again. Do *not* uncomment `incbin "dte.bin"`: the DTE table is written by
`som.py insert_misc`, and the `incbin` would overwrite it.

### `table.asm`
Not run on its own. It is the character table used by `menus.asm`
(`'a' = $81`, `'A' = $9B`, …). This is the **menu** character set, different
from the dialogue one. Include it when you write text with `db "..."`.

### `menus.asm` — menus, status screen, shops
Applied to the ROM. It replaces the hardcoded English menu strings with
Italian ones written at the end of the file, and moves a few things around so
the longer words fit (extra space before weapon and magic names, blacksmith
line positions, `GP` → `PO`, `EMPTY` → `Vuoto`).

**To change a menu word**: edit the strings in the "Free space" section at the
bottom (`ExpString`, `LevelString`, `MPString`, …). The last line
`assert pc() < $C74350` makes asar fail if your strings become too long: the
area `$C74290`–`$C74350` (192 bytes) is all you have, because `$C74350` is the
DTE table.

Some strings are written as raw bytes because they are only 2 characters
(for example `lda #$9FA8` = `NE`, `lda #$A9AA` = `PO`). To change those, look up
the byte values in `table.asm`.

### `intro_table.asm`
The character table of the **intro** only (`'A' = $61`, `'.' = $7B`, …).
Included by `intro.asm`.

### `intro.asm` — intro text, credits, error messages
Applied to the ROM. It writes the intro texts at `$CB3400`:

```asm
; db $06,"DARKNESS SWEEPS THE",$00
db $01,"LE TENEBRE AVVOLGONO IL MONDO,",$00
db $01,$00
```

* the **first byte** is how many spaces to put before the line: this is how you
  centre the text (the original English line is kept commented above);
* `$00` closes the line;
* `db $01,$00` is an empty line;
* a line is **32 tiles** wide (leading spaces + text), so keep the text at 30
  characters or less; the comments at the bottom of the file show the finished
  lines already centred, use them to count.

Sections: `IntroText` (`$CB3400`), `MultitapError` (`$CB3600`), `Credits`
(`$CB3680`), `RegionError` (`$CB3700`). Everything must stay before `$CB3800`,
where text block 5 starts.

### `intro_ram.asm` — the intro routine
This one is **not** applied to the ROM. It is assembled onto
`translated_misc/intro-code.bin`, the decompressed intro routine, which is then
recompressed and put back in the ROM by `insert_misc`.

It tells the intro where to read the text from: instead of the original
addresses, it reads from `$CB3400`, i.e. the strings written by `intro.asm`,
and it fixes the pointers of the credits, the empty line, the multitap error
and the region error.

You normally do not need to touch it. You do if you move a block in
`intro.asm`: then the `ldx #$....` values here must be updated
(they are offsets from `$CB3400`).

---

## 11. "I want to change…"

| What | Where |
| --- | --- |
| Dialogue, item, spell, monster names | dump `.txt` → database → `insert_text` |
| Battle and shop messages | same, blocks 7 and 8 |
| Status and weapon names | same, blocks 3 and 6 |
| Menu labels (LEVEL, EXP, HP/MP, GP, EMPTY) | `asm/menus.asm` |
| Intro text, credits, error messages | `asm/intro.asm` |
| Font (character shapes) | `asm/font.bin` (+ `.tbl` if you add characters) |
| Accented letters | `asm/font.bin` + `som_main_ita.tbl` / `som_main_with_dte_ita.tbl` |
| DTE pairs | `translated_misc/dte.csv` + the `_ita` `.tbl` files |
| Menu icons with text | `translated_gfx/menu_icon_*.bin` |
| Intro image / "THE END" screen | `translated_misc/intro-tilemap.bin`, `the-end-gfx.bin`, `the-end-tilemap.bin` (see `tilesets/*.png`) |
| Compass letters (N/S/E/W) | `translated_misc/7FB00_cardinals.bin` (160 bytes) |

---

## 12. Free space map

The ROM is HiROM: the file offset is the SNES address minus `$C00000`.
So `$C74350` in the ASM files is `0x74350` in the ROM file.

| File offset | SNES address | Used by | Size |
| --- | --- | --- | --- |
| `0x74290` | `$C74290` | `menus.asm` strings | 192 bytes (until `0x74350`) |
| `0x74350` | `$C74350` | DTE table (`insert_misc`) | 138 bytes (69 pairs) |
| `0x74400` | `$C74400` | Font (`font.bin`) | 1152 bytes |
| `0x74900` | `$C74900` | Text blocks 3, 4, 6 | 1792 bytes |
| `0xB3400` | `$CB3400` | Intro texts (`intro.asm`) | 1024 bytes (until `0xB3800`) |
| `0xB3800` | `$CB3800` | Text block 5 | 2048 bytes |

The intro texts and text block 5 are neighbours: if the intro strings grow past
`0xB3800` they eat the tutorial messages.

---

## 13. Things that go wrong

* **`Command 'asar' not found`** — install asar and put it in your PATH.
* **`ERROR: BLOCK OVERFLOW at ID …`** — that block is full. Shorten the text or
  add DTE pairs.
* **`Text size exceeds!`** — more than 69 DTE rows in `dte.csv`.
* **asar `assert` failed in `menus.asm`** — the menu strings passed `$C74350`
  and would eat the DTE table. Shorten them.
* **Garbled text in game** — `dte.csv` and the `_ita.tbl` do not match, or you
  translated with a `.tbl` that is not the one used to insert.
* **My translation is not in the ROM** — you edited the `.txt` but did not run
  `_import_translation.sh`; the inserter reads only the database.
* **The whole ROM comes out in English, with no error** — the `-u` author has
  no translations in the database. The query is a `LEFT JOIN`, so an unknown
  author still returns every line, with an empty translation, and the inserter
  falls back to the English text. Check `USER=` at the top of `som.sh` and that
  you imported your work under that same name.
* **`translated_misc/intro-code.bin` and `intro-data.bin` must exist** before
  running the insert part: they are the copies of the files in `dump_misc/`
  that asar and `insert_tilemap` edit in place.

---

## 14. The other two scripts

| Script | What it is for |
| --- | --- |
| `bin/som_pal.sh` | Same process on the European ROM, using `som_pal.py`. The only real differences are the ROM name and the intro data offset (`0x7B478` instead of `0x7B480`) |
| `bin/som_sadnes.sh` | Only dumps: it reads the old SADNES Italian translation into `translated_text_sadnes/`, to compare it with yours. It never writes a ROM |

There is also `../brainlordresources/som/check_length.py`, which lists the
monster names (ID 2256–2383) and status messages (ID 2625–2646) longer than
28 characters.
