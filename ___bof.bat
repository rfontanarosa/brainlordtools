set USER="clomax"
set DB="./resources/bof/db/bof.db"
set SOURCE="./resources/bof/roms/Breath of Fire (U) [!].sfc"
set DESTINATION="./resources/bof/roms/Breath of Fire (I) [!].sfc"
set MISC="./resources/bof/misc.csv"
set TABLE1="./resources/bof/tables/Breath of Fire (U) [!].tbl"
set TABLE2="./resources/bof/tables/Breath of Fire (I) [!].tbl"
set TABLE3="./resources/bof/tables/Breath of Fire (U) [!].base.tbl"

REM python _bof.py --mte_finder -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

python _bof.py --crc32check --dump -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%
REM python _bof.py --mte_optimizer -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2% -t3 %TABLE3%
REM python _bof.py --insert -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%
REM python _bof.py --insert_misc -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -m %MISC% -t1 %TABLE1% -t2 %TABLE2% -t3 %TABLE3%

pause
