set SOURCE="soe/resources/roms/rom.smc"
set DESTINATION="soe/resources/roms/rom1.smc"
set TABLE1="soe/resources/tables/soe.tbl"

python _soe.py --dump -s %SOURCE% -d %DESTINATION% -t1 %TABLE1%
python _soe.py --insert -s %SOURCE% -d %DESTINATION% -t1 %TABLE1%

pause