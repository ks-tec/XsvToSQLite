# Import from csv/tsv/psv file to SQLite3 database.
#
# Copyright (c) 2020 ks-tec
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to dealin the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sellcopies of the Software, and to permit persons to whom the Software
# is furnished to do so, subject to the following conditions:
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE NOT LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS INTHE SOFTWARE.


import os, sys, csv, sqlite3, traceback, argparse
from collections import namedtuple


class XsvToSQLite():
  """
  Import data from XSV file to SQLite3 database.
  """

  # set isolation level namedtuple
  #   IsolationLevel.DEFERRED  : The first read operation against a database creates a SHARED lock and the first write operation creates a RESERVED lock.
  #   IsolationLevel.IMMEDIATE : RESERVED locks are acquired on all databases as soon as the BEGIN command is executed, without waiting for the database to be used.
  #   IsolationLevel.EXCLUSIVE : No other database connection except for read_uncommitted connections will be able to read the database and no other connection without exception will be able to write the database until the transaction is complete.
  Isolation = namedtuple('Isolation', 'DEFERRED, IMMEDIATE, EXCLUSIVE')
  IsolationLevel = Isolation('DEFERRED', 'IMMEDIATE', 'EXCLUSIVE')

  def __init__(self, import_source_file, target_db_name, target_db_table, is_header_skip=False, is_create_table=False, sql_create_table=None):
    """
    Constructor of XsvToSQLite class.
    The source file should be csv (comma separated value), tsv (tab separated value), psv (pipe separated value).

    Args:
      import_source_file: source file name to import
      target_db_name:     database name to import to
      target_db_table:    table name to import to
      is_header_skip:     skip for header line, True is skip, or False is non-skip
      is_create_table:    create or recreate for new table, True is coreate or recreate, False is non-create or non-recreate
      sql_create_table:   DDL query for create table to import to
    """
    print(self.__class__.__name__ + ' initializing, and instantiating.')

    self.target_db_name     = target_db_name
    self.target_db_table    = target_db_table
    self.import_source_file = import_source_file
    self.is_header_skip     = is_header_skip
    self.is_create_table    = is_create_table

    # set delimiter from file extension.
    _, raw_delimiter = os.path.splitext(import_source_file)
    if raw_delimiter == '.csv':
      self.delimiter = ','
    elif raw_delimiter == '.tsv':
      self.delimiter = '\t'
    elif raw_delimiter == '.psv':
      self.delimiter = '|'
    else:
      raise ValueError('Import source file should be csv ,tsv, or psv.')

    # set table creation DDL
    self.sql_create_table = sql_create_table

    # if is_create_table is True and is_header_skip is False,
    # and also if sql_create_table is None, raise ValueError.
    if self.is_create_table:
      if not self.is_header_skip:
        if not sql_create_table:
          raise ValueError('It\'s necessary SQL to create table.')

  def begin(self, cur, isolation_level=IsolationLevel.DEFERRED):
    """
    begin transaction.
    isolation level is optional, and can specify value of 'DEFERRED', 'IMMEDIATE', or 'EXCLUSIVE'.

    Args:
      cur:  cursor object of database connection
      isolation_level:  transaction isolation level, 'DEFERRED', 'IMMEDIATE', or 'EXCLUSIVE'
    """
    print(self.begin.__name__ + ': Begining Transaction. (' + isolation_level + ')')

    cur.execute('begin ' + isolation_level)

  def insert_from_file(self, cur):
    """
    import data to SQLite database.
    if both is_create_table and is_header_skip is True, both the table creation DDL query is created and executed automatically.

    Args:
      cur:  cursor object of database connection
    """
    print(self.insert_from_file.__name__ + ': Inserting all data from file.')

    header, data = self.read_import_file()

    if self.is_create_table:
      if self.is_header_skip:
        self.make_create_query(header)
      self.create_from_ddl(cur)

    column_cnt = self.count_column_nums(data)
    column_names = ['?' for i in range(column_cnt)]
    cur.executemany("insert into {0} values ({1})".format(self.target_db_table, ','.join(column_names)), data)

    print(self.insert_from_file.__name__ + ': Complete of insert all data.')

  def read_import_file(self):
    """
    reading source file to import, set import data to list object.

    Return:
      list object of import data
    """
    print(self.read_import_file.__name__ + ': Reading data from import source.')

    header = None
    data   = None

    with open(self.import_source_file, 'r', encoding='utf-8') as f:
      reader = csv.reader(f, delimiter=self.delimiter)
      if self.is_header_skip:
        header = next(reader)

      data = [i for i in reader]
    
    return header, data

  def make_create_query(self, import_header):
    """
    create the table creation DDL query to import to.
    the table creation DDL built by header line of source file overwrite original DDL.

    Args:
      import_header:  one-dimensional list of items in header row
    """
    print(self.make_create_query.__name__ + ': Creating the table creation DDL.')

    if not import_header:
      raise ValueError('It\'s necessary of header to import.')
    
    sql = "create table " + self.target_db_table + " ("
    sql += ", ".join(["{} text".format(col) for col in import_header])
    sql += ");"

    self.sql_create_table = sql

  def create_from_ddl(self, cur):
    """
    create table on SQLite database from specified DDL query.

    Args:
      cur:  cursor object of database connection
    """
    print(self.create_from_ddl.__name__ + ': Droping and creating table.')

    cur.execute('drop table if exists {};'.format(self.target_db_table))
    cur.execute(self.sql_create_table)

  def count_column_nums(self, import_data):
    """
    count number of columns from source file to import.

    Args:
      import_data:  two-dimensional list of items in data rows

    Return:
      count of columns
    """
    print(self.count_column_nums.__name__ + ': Counting columns number.')

    # count number of columns in each row.
    # if the number of columns is different, raise ValueError.
    columns = [len(row) for row in import_data]
    if len(set(columns)) != 1:
      raise ValueError('this import files has different column numbers.')

    return columns[0]


if __name__ == '__main__':
  """
  Entry point at functional execution.
  """
  # parse arguments from command line parameters
  p = argparse.ArgumentParser()
  p.description = 'the data in source file will be imported to SQLite database.'
  p.add_argument('-s',  '--source_file',      type=str,            help='import source file')
  p.add_argument('-o',  '--output_database',  type=str,            help='output database file')
  p.add_argument('-t',  '--output_table',     type=str,            help='create table name')
  p.add_argument('-cs', '--is_create_table',  action='store_true', help='is create table')
  p.add_argument('-hs', '--is_header_skip',   action='store_true', help='is header skip')
  p.add_argument('-d',  '--ddl_create_table', type=str,            help='table creation ddl')

  args = p.parse_args()
  print()

  try:
    # instantiate of XsvToSQLite class.
    sql = XsvToSQLite(
      import_source_file = args.source_file,
      target_db_name     = args.output_database,
      target_db_table    = args.output_table,
      is_header_skip     = args.is_header_skip,
      is_create_table    = args.is_create_table,
      sql_create_table   = args.ddl_create_table
    )
    conn = None

    try:
      # open the connection to SQLite3 database
      conn = sqlite3.connect(sql.target_db_name)
      cur = conn.cursor()

      # begin transaction
      # sql.begin(cur)
      # sql.begin(cur, sql.IsolationLevel.DEFERRED)
      sql.begin(cur, sql.IsolationLevel.IMMEDIATE)
      # sql.begin(cur, sql.IsolationLevel.EXCLUSIVE)

      # import data to SQLite3 database
      sql.insert_from_file(cur)

      # commit changes to SQLite3 database
      conn.commit()
      print('\nWork is complete.')

    except sqlite3.Error as err:
      # rollback changes to SQLite3 database
      if conn: conn.rollback()

      # sqlite3.Error has occured
      print('\nA sqlite3.Error has occured.')
      traceback.print_exc()

    finally:
      # close the connection to SQLite3 database
      if conn: conn.close()

  except Exception as ex:
    # any exception has occured
    print('\nAn any exeption has occured.')
    traceback.print_exc()

  finally:
    print()
