set RESOURCE_PATH=./resources/bof

set USER=clomax
set DUMP_PATH=%RESOURCE_PATH%/dump
set DB=%RESOURCE_PATH%/db/bof.db
set SOURCE="%RESOURCE_PATH%/roms/Breath of Fire (U) [!].sfc"
set DESTINATION="%RESOURCE_PATH%/roms/Breath of Fire (I) [!].sfc"
set MISC="%RESOURCE_PATH%/misc.csv"
set TABLE1="%RESOURCE_PATH%/tables/Breath of Fire (U) [!].tbl"
set TABLE2="%RESOURCE_PATH%/tables/Breath of Fire (I) [!].tbl"
set TABLE3="%RESOURCE_PATH%/tables/Breath of Fire (U) [!].base.tbl"
set MTE_OPTIMIZER_PATH="%RESOURCE_PATH%/../.."
set TEMP_PATH="%RESOURCE_PATH%/../../temp"

REM python _bof.py mte_finder -s "%SOURCE%" -t1 "%TABLE1%"
python _bof.py dump -s "%SOURCE%" -t1 "%TABLE1%" -dp "%DUMP_PATH%" -db "%DB%"
REM python _bof.py mte_optimizer -d "%DESTINATION%" -t1 "%TABLE1%" -t2 "%TABLE2%" -t3 "%TABLE3%" -tp "%TEMP_PATH%" -mop "%MTE_OPTIMIZER_PATH%" -db "%DB%" -u "%USER%"
REM python _bof.py insert -d "%DESTINATION%" -t2 "%TABLE2%" -db "%DB%" -u "%USER%"
REM python _bof.py insert_misc -d "%DESTINATION%" -m1 "%MISC%" -t3 "%TABLE3%"

pause
