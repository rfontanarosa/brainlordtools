set USER="clomax"
set DB="./resources/bof/db/bof.db"
set SOURCE="./resources/bof/gemini/roms/bof.smc"
set DESTINATION="./resources/bof/gemini/roms/bof-ita.smc"
set MISC="./resources/bof/misc.csv"
REM set DESTINATION="./resources/bof/gemini/roms/bof-ita1.smc"
REM set MISC="./resources/bof/misc1.csv"
set TABLE1="./resources/bof/tables/Breath of Fire (U) [!].tbl"
set TABLE2="./resources/bof/tables/Breath of Fire (I) [!].tbl"
set TABLE3="./resources/bof/tables/Breath of Fire (U) [!].base.tbl"

REM python _bof-gemini.py --mte_optimizer -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2% -t3 %TABLE3%
REM python _bof-gemini.py --insert -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%
REM python _bof.py --insert_misc -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -m %MISC% -t1 %TABLE1% -t2 %TABLE2% -t3 %TABLE3%

pause
