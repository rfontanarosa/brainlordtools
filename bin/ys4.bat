set RESOURCE_PATH=../resources/ys4

set USER=clomax
set DUMP_PATH=%RESOURCE_PATH%/dump
set DB=%RESOURCE_PATH%/db/ys4.db
set SOURCE="%RESOURCE_PATH%/roms/Ys IV - Mask of the Sun (U).sfc"
set DESTINATION="%RESOURCE_PATH%/roms/Ys IV - Mask of the Sun (I).sfc"
set TABLE1="%RESOURCE_PATH%/tables/Ys IV - Mask of the Sun (U).tbl"
set TABLE2="%RESOURCE_PATH%/tables/Ys IV - Mask of the Sun (I).tbl"
set TABLE3="%RESOURCE_PATH%/tables/Ys IV - Mask of the Sun.base.tbl"
set MTE_OPTIMIZER_PATH="%RESOURCE_PATH%/../.."
set TEMP_PATH="%RESOURCE_PATH%/../../temp"

REM python ../brainlordtools/ys4.py mte_finder -s %SOURCE% -t1 %TABLE1%
python ../brainlordtools/ys4.py dump -s %SOURCE% -t1 %TABLE1% -dp %DUMP_PATH% -db %DB%
REM python ../brainlordtools/ys4.py mte_optimizer -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2% -t3 %TABLE3% -tp %TEMP_PATH% -mop %MTE_OPTIMIZER_PATH% -db %DB% -u %USER%
REM python ../brainlordtools/ys4.py insert -d %DESTINATION% -t1 %TABLE1% -db %DB% -u %USER%

pause
