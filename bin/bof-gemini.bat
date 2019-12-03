set RESOURCE_PATH=../resources/bof

set USER=clomax

set DB=%RESOURCE_PATH%/db/bof.db
set SOURCE="%RESOURCE_PATH%/gemini/roms/bof.smc"
set DESTINATION="%RESOURCE_PATH%/gemini/roms/bof-ita.smc"
set MISC="%RESOURCE_PATH%/misc.csv"
REM set DESTINATION="%RESOURCE_PATH%/gemini/roms/bof-ita1.smc"
REM set MISC="%RESOURCE_PATH%/bof/misc1.csv"
set TABLE1="%RESOURCE_PATH%/tables/Breath of Fire (U) [!].tbl"
set TABLE2="%RESOURCE_PATH%/tables/Breath of Fire (I) [!].tbl"
set TABLE3="%RESOURCE_PATH%/tables/Breath of Fire (U) [!].base.tbl"
set MTE_OPTIMIZER_PATH="%RESOURCE_PATH%/../.."
set TEMP_PATH="%RESOURCE_PATH%/../../temp"

REM python ../brainlordtools/bof.py mte_optimizer -d "%DESTINATION%" -t1 "%TABLE1%" -t2 "%TABLE2%" -t3 "%TABLE3%" -tp "%TEMP_PATH%" -mop "%MTE_OPTIMIZER_PATH%" -db "%DB%" -u "%USER%"
REM python ../brainlordtools/bof-gemini.py insert -d "%DESTINATION%" -t2 "%TABLE2%" -db "%DB%" -u "%USER%"
REM python ../brainlordtools/bof.py insert_misc -d "%DESTINATION%" -m1 "%MISC%" -t3 "%TABLE3%"

pause
