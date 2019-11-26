set USER="clomax"
set DB="./resources/ys4/db/ys4.db"
set SOURCE="./resources/ys4/roms/Ys IV - Mask of the Sun (U).sfc"
set DESTINATION="./resources/ys4/roms/Ys IV - Mask of the Sun (I).sfc"
set TABLE1="./resources/ys4/tables/Ys IV - Mask of the Sun (U).tbl"
set TABLE2="./resources/ys4/tables/Ys IV - Mask of the Sun (I).tbl"
set TABLE3="./resources/ys4/tables/Ys IV - Mask of the Sun.base.tbl"

REM python _ys4.py --mte_finder -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

python _ys4.py --crc32check --dump -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%
REM python _ys4.py --mte_optimizer -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2% -t3 %TABLE3%
REM python _ys4.py --insert -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

pause
