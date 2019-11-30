set RESOURCE_PATH=./resources/ys3

set USER=clomax
set DUMP_PATH=%RESOURCE_PATH%/dump
set DB=%RESOURCE_PATH%/db/ys3.db
set SOURCE="%RESOURCE_PATH%/roms/Ys III - Wanderers from Ys (U) [!].smc"
set DESTINATION="%RESOURCE_PATH%/roms/Ys III - Wanderers from Ys (I) [!].smc"
set TABLE1="%RESOURCE_PATH%/tables/Ys III - Wanderers from Ys (U) [!].tbl"
set TABLE2="%RESOURCE_PATH%/tables/Ys III - Wanderers from Ys (U) [!].tbl"

python _ys3.py dump -s %SOURCE% -t1 %TABLE1% -dp %DUMP_PATH% -db %DB%
REM python _ys3.py insert -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2% -db %DB% -u %USER%

pause
