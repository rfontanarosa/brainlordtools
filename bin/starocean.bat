set HOME=C:\Users\rober

set BRAINLORD_PATH=%HOME%/git
set RESOURCE_PATH=%BRAINLORD_PATH%/brainlordresources/starocean
set TOOLS_PATH=%BRAINLORD_PATH%/brainlordtools/brainlordtools

set SOURCE_ES="%RESOURCE_PATH%/roms/Star_Ocean_ES.sfc"

set TABLE1=%RESOURCE_PATH%/tables/star_ocean_ES_small.tbl

set DUMP_MISC_PATH=%RESOURCE_PATH%/dump_misc

python %TOOLS_PATH%/starocean.py dump_misc -s %SOURCE_ES% -t1 %TABLE1% -dp %DUMP_MISC_PATH%
