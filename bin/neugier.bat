set RESOURCE_PATH=../resources/neugier

set USER=clomax
set DUMP_PATH=%RESOURCE_PATH%/dump
set DB=%RESOURCE_PATH%/db/neugier.db
set SOURCE="%RESOURCE_PATH%/roms/Neugier (J) [T+Eng2.00_Haeleth&RPGOne].sfc"
set DESTINATION="%RESOURCE_PATH%/roms/Neugier - Umi to Kaze no Kodou (I).sfc"
set TABLE1="%RESOURCE_PATH%/tables/Neugier - Umi to Kaze no Kodou (U).tbl"
set TABLE2="%RESOURCE_PATH%/tables/Neugier - Umi to Kaze no Kodou (I).tbl"

python ../brainlordtools/neugier.py dump -s %SOURCE% -t1 %TABLE1% -dp %DUMP_PATH% -db %DB%
REM python ../brainlordtools/python neugier.py insert -d %DESTINATION% -t2 %TABLE2% -db %DB% -u %USER%

pause
