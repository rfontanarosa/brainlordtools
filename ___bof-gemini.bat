set USER="clomax"
set DB="bof/db/bof.db"
set SOURCE="bof/gemini/roms/bof.smc"
set DESTINATION="bof/gemini/roms/bof-ita.smc"
set MISC="bof/misc.csv"
REM set DESTINATION="bof/gemini/roms/bof-ita1.smc"
REM set MISC="bof/misc1.csv"
set TABLE1="bof/tables/Breath of Fire (U) [!].tbl"
set TABLE2="bof/tables/Breath of Fire (I) [!].tbl"
set TABLE3="bof/tables/Breath of Fire (U) [!].base.tbl"

REM python _bof-gemini.py --mte_optimizer -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2% -t3 %TABLE3%
REM python _bof-gemini.py --insert -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%
REM python _bof.py --insert_misc -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -m %MISC% -t1 %TABLE1% -t2 %TABLE2% -t3 %TABLE3%

pause
