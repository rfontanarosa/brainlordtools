set USER="clomax"
set DB="./resources/brandish2/db/brandish2.db"
set SOURCE="./resources/brandish2/roms/Brandish 2 (U) [!].smc"
set DESTINATION="./resources/brandish2/roms/Brandish 2 (I) [!].smc"
set TABLE1="./resources/brandish2/tables/Brandish 2 (U) [!].tbl"
set TABLE2="./resources/brandish2/tables/Brandish 2 (I) [!].tbl"

python _brandish2.py --crc32check --dump -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%
REM python _brandish2.py --insert -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

pause
