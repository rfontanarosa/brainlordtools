set RESOURCE_PATH=../resources/soe

set DUMP_PATH=%RESOURCE_PATH%/dump
set TRANSLATION_PATH=%RESOURCE_PATH%/translation
set SOURCE=%RESOURCE_PATH%/roms/evermore.sfc
set DESTINATION=%RESOURCE_PATH%/roms/patched_evermore.sfc
set TABLE1=%RESOURCE_PATH%/tables/soe.tbl
set MISC1=%RESOURCE_PATH%/misc.csv
set DUMP_GFX_PATH=%RESOURCE_PATH%/dump_gfx

python ../brainlordtools/soe.py dump -s %SOURCE% -t1 %TABLE1% -dp %DUMP_PATH%
python ../brainlordtools/soe.py insert -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -tp %TRANSLATION_PATH% -m1 %MISC1%
python ../brainlordtools/soe.py dump_gfx -s %SOURCE% -dp %DUMP_GFX_PATH%
python ../brainlordtools/soe.py insert_gfx -d %DESTINATION% -tp %TRANSLATION_PATH%

pause
