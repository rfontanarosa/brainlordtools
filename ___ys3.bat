set USER="clomax"
set DB="./resources/ys3/db/ys3.db"
set SOURCE="./resources/ys3/roms/Ys III - Wanderers from Ys (U) [!].smc"
set DESTINATION="./resources/ys3/roms/Ys III - Wanderers from Ys (I) [!].smc"
set TABLE1="./resources/ys3/tables/Ys III - Wanderers from Ys (U) [!].tbl"
set TABLE2="./resources/ys3/tables/Ys III - Wanderers from Ys (U) [!].tbl"

python _ys3.py --crc32check --dump -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%
REM python _ys3.py --insert -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

pause
