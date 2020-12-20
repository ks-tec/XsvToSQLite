@echo off

rem the following call is for showing arguments help at running.
rem python XsvToSQLite.py -h

rem the following call is for importing csv formated file to SQLite3 database.
python XsvToSQLite.py ^
  --source_file=..\prefecture_code.csv ^
  --output_database=..\prefecture_code.db ^
  --output_table=prefecture_code ^
  --is_header_skip ^
  --is_create_table ^
  --ddl_create_table="hoge"
