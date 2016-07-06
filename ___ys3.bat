set USER="clomax"
set DB="ys3/db/ys3.db"
set SOURCE="ys3/roms/Ys III - Wanderers from Ys (U) [!].smc"
set DESTINATION="ys3/roms/Ys III - Wanderers from Ys (I) [!].smc"
set TABLE1="ys3/tables/Ys III - Wanderers from Ys (U) [!].tbl"
set TABLE2="ys3/tables/Ys III - Wanderers from Ys (U) [!].tbl"
set TABLE3="ys3/tables/Ys III - Wanderers from Ys (U) [!].tbl"

REM python _ys3.py --crc32check --dump -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%
python _ys3.py --insert -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

pause