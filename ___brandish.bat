set RESOURCE_PATH=./resources/brandish

set USER=clomax
set DUMP_PATH=%RESOURCE_PATH%/dump
set DB=%RESOURCE_PATH%/db/brandish.db
set SOURCE="%RESOURCE_PATH%/roms/Brandish (U) [!].smc"
set DESTINATION="%RESOURCE_PATH%/roms/Brandish (I) [!].smc"
set TABLE1="%RESOURCE_PATH%/tables/Brandish (U) [!].tbl"
set TABLE2="%RESOURCE_PATH%/tables/Brandish (I) [!].tbl"

python _brandish.py dump -s %SOURCE% -t1 %TABLE1% -dp %DUMP_PATH% -db %DB%
REM python _brandish.py insert -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2% -db %DB% -u %USER%

pause
