set RESOURCE_PATH=../resources/brandish2

set USER=clomax
set DUMP_PATH=%RESOURCE_PATH%/dump
set DB=%RESOURCE_PATH%/db/brandish2.db
set SOURCE="%RESOURCE_PATH%/roms/Brandish 2 (U) [!].smc"
set DESTINATION="%RESOURCE_PATH%/roms/Brandish 2 (I) [!].smc"
set TABLE1="%RESOURCE_PATH%/tables/Brandish 2 (U) [!].tbl"
set TABLE2="%RESOURCE_PATH%/tables/Brandish 2 (I) [!].tbl"

python ../brainlordtools/brandish2.py dump -s %SOURCE% -t1 %TABLE1% -dp %DUMP_PATH% -db %DB%
REM python ../brainlordtools/brandish2.py insert -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2% -db %DB% -u %USER%

pause
