# XsvToSQLite

## Overview
This project is developed in Python 3.7.7 with Visual Studio Code on Windows 10.  

The format of import source file should be csv, tsv, or psv.  
And, the data in source file will be imported to SQLite database.  

## Installation
You download this project files from GitHub repository.  
And put the dowonload project to your any directory.  

```
> cd your-directory

> git clone https://github.com/ks-tec/XsvToSQLite

```

## Settings
You can change setting value according to your environment.  
They are set directly in "main.py".  

```
########## change params here ##########
import_source_file = 'C:\\VSCode\\Projects\\prefecture_code.csv'
target_db_name     = 'C:\\VSCode\\Projects\\prefecture_code.db'
target_db_table    = 'prefecture'
is_header_skip     = True
is_create_table    = True
sql_create_table   = None
########################################
```

The following is supported format of XSV data file.  

| file type | file extension | data delimiter | ASCII code |
| ---- | ---- | ---- | ---- |
| comma separated value | csv | , | 0x2c |
| tab separated value | tsv | \t | 0x09 |
| pipe separated value | psv | \| | 0x7c |

In addition, if you set `is_create_table` set True and `is_header_skip` set True, `sql_create_table` is built from header row, and is automatic droped and created.  
But, if you set `is_create_table` set True and `is_header_skip` set False, `sql_create_table` must set DDL (Data Definition Language) with SQL (Structured Query Language).  

| is_create_table | is_header_skip | sql_create_table | creating a table to import to |
| ---- | ---- | ---- | ---- |
| True | True | not necessary and not valid | automatic table creation from header row |
| True | False | necessary | should be specified a table creation DDL |
| False | True | not valid | use existing table and append data |
| False | False | not valid | use existing table and append data |

## Constraintion

The imported table has no key columns.  
This is because the key columns of the source file to be imported cannot be determined.  
And, In general, key columns cannot be represented in XSV file.  

This is by design.  

## Running Example
The following is an example of this project run.  

```
> cd C:\VSCode\Projects\XsvToSQLite

> dir ../

    directory: C:\VSCode\Projects

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       2020/12/17     12:20                XsvToSQLite
-a----       2020/12/16     18:44            689 prefecture_code.csv

> python main.py
XsvToSQLite initializing, and instantiating.
begin: Begining Transaction. (IMMEDIATE)
insert_from_file: Inserting all data from file.
read_import_file: Reading data from import source.
make_create_query: Creating the table creation DDL.
create_from_ddl: Droping and creating table.
count_column_nums: Counting columns number.
insert_from_file: Complete of insert all data.

Work is complete.

> dir ../

    directory: C:\VSCode\Projects

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       2020/12/17     12:20                XsvToSQLite
-a----       2020/12/16     18:44            689 prefecture_code.csv
-a----       2020/12/17     12:31           8192 prefecture_code.db
```

## Change log

### 1.0.2
Defined IsolationLevel by namedtuple.

### 1.0.1
Explicitly start a transaction.  
And, that was achieved by adding method 'begin' to XsvToSQLite class.  

### 1.0.0
First release.  
This project is developed in Python 3.7.7.  

## License ライセンス
This project is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).  
Copyright (c) 2020, [ks-tec](https://github.com/ks-tec/).  
