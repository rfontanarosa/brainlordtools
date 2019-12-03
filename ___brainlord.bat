set RESOURCE_PATH=./resources/brainlord

set USER=clomax
set DUMP_PATH=%RESOURCE_PATH%/dump
set DB=%RESOURCE_PATH%/db/brainlord.db
set SOURCE="%RESOURCE_PATH%/roms/Brain Lord (U) [!].smc"
set DESTINATION="%RESOURCE_PATH%/roms/Brain Lord (I) [!].smc"
set TABLE1="%RESOURCE_PATH%/tables/Brain Lord (U) [!].tbl"
set TABLE2="%RESOURCE_PATH%/tables/Brain Lord (U) [!].tbl"

python _brainlord.py dump -s %SOURCE% -t1 %TABLE1% -dp %DUMP_PATH% -db %DB%
REM python _brainlord.py insert -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2% -db %DB% -u %USER%

pause
