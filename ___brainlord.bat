set USER="clomax"
set DB="brainlord/db/brainlord.db"
set SOURCE="brainlord/roms/Brain Lord (U) [!].smc"
set DESTINATION="brainlord/roms/Brain Lord (I) [!].smc"
set TABLE1="brainlord/tables/Brain Lord (U) [!].tbl"
set TABLE2="brainlord/tables/Brain Lord (U) [!].tbl"

python _brainlord.py --crc32check --dump -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

pause