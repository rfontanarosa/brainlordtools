set USER="clomax"
set DB="brandish/db/brandish.db"
set SOURCE="brandish/roms/Brandish (U) [!].smc"
set DESTINATION="brandish/roms/Brandish (I) [!].smc"
set TABLE1="brandish/tables/Brandish (U) [!].tbl"
set TABLE2="brandish/tables/Brandish (I) [!].tbl"

python _brandish.py --crc32check --dump -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%
REM python _brandish.py --insert -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

pause