set USER="clomax"
set DB="bof/db/bof.db"
set SOURCE="bof/gba/roms/0245 - Breath of Fire (I).gba"
set TABLE1="bof/gba/tables/0245 - Breath of Fire (U).tbl"

python _bof-gba.py --dump -s %SOURCE% -t1 %TABLE1%

pause