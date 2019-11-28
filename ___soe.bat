set RESOURCE_PATH=./resources/soe

set SOURCE=%RESOURCE_PATH%/roms/evermore.sfc
set DESTINATION=%RESOURCE_PATH%/soe/roms/patched_evermore.sfc
set TABLE1=%RESOURCE_PATH%/tables/soe.tbl

python _soe.py --dump -s %SOURCE% -d %DESTINATION% -t1 %TABLE1%
python _soe.py --insert -s %SOURCE% -d %DESTINATION% -t1 %TABLE1%

pause
