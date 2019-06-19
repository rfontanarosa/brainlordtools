set USER="clomax"
set DB="bof/db/bof.db"
set SOURCE="bof/gemini/roms/bof.smc"
set DESTINATION="bof/gemini/roms/bof-ita.smc"
set TABLE1="bof/tables/Breath of Fire (U) [!].tbl"
set TABLE2="bof/tables/Breath of Fire (I) [!].tbl"
set TABLE3="bof/tables/Breath of Fire (U) [!].base.tbl"

python _bof-gemini.py --mte_optimizer -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2% -t3 %TABLE3%
python _bof-gemini.py --insert -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

pause