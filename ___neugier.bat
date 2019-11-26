set USER="clomax"
set DB="./resources/neugier/db/neugier.db"
set SOURCE="./resources/neugier/roms/Neugier (J) [T+Eng2.00_Haeleth&RPGOne].sfc"
set DESTINATION="./resources/neugier/roms/Neugier - Umi to Kaze no Kodou (I).sfc"
set TABLE1="./resources/neugier/tables/Neugier - Umi to Kaze no Kodou (U).tbl"
set TABLE2="./resources/neugier/tables/Neugier - Umi to Kaze no Kodou (I).tbl"

python _neugier.py --crc32check --dump -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%
REM python _neugier.py --insert -u %USER% -db %DB% -s %SOURCE% -d %DESTINATION% -t1 %TABLE1% -t2 %TABLE2%

pause
