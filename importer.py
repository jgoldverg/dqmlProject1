"""Sona460 DMQL Project

Usage:
    importer.py load_csv <file_path>
    importer.py get_date [--year=year_covid --month=month_covid --day=day_covid [default: --year=0, --month=0, --day=0]]
    importer.py drop_table <tablename>
    importer.py drop_column <tablename> <columnname>
    importer.py alter_covid_table
    importer.py stats <state> <column_name>
    importer.py print_table_stats [--table_name=table_name] 
    importer.py sign_up --username=username --password=password
    importer.py sign_in --username=username --password=password

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  --year=year_covid         The year you are searching for [default: 2020]
  --day=day_covid           The day [default: 0]
  --month=month_covid       The month [default: 0]
  --table_name=table_name   The name of the table you wish to use [default: coviddays]
  start-date                Is of form "year-month-day hr:min:sec"
  end-date                  Is of form "year-month-day hr:min:sec"
  year                      The year you want to aggregate results from
  file_path                 An absolute path to the csv file from John Hopkins you wish to read into postgres
  sign_in                   This takes a username and a password and if the user exists assigns a local environment variable that is the connection string. This way the cli will use that specific connection string for a user.
"""

from os import stat
from os import environ
from os.path import exists
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import inspect
import psycopg2
import io
from docopt import docopt
import pprint

class Sona460:
    def get_options(self, conn, engine, inspector):
        self.args = docopt(__doc__)
        user_conn = conn
        user_engine = engine
        user_inspector = inspector

        if self.args['sign_in']:
            username = self.args['--username']
            if check_if_user_exists(conn, username):
                engine, conn, inspector = build_db_conn(create_connection(username, self.args['--password']))
        if self.args['load_csv']:
            load_from_csv(engine.raw_connection(), engine, self.args["<file_path>"])
        elif self.args['get_date']:
            get_date(conn, self.args['--year'][0],self.args['--month'][0], self.args['--day'][0])
        elif self.args['drop_table']:
            drop_table(self.args["<tablename>"], conn)
        elif self.args['drop_column']:
            drop_column(self.args["<tablename>"], self.args["<columnname>"], conn)
        elif self.args['alter_covid_table']:
            make_covid_days_unique_constraint_and_primary_key(conn, inspector)
        elif self.args['stats']:
            print_stats(conn, self.args["<state>"], self.args["<column_name>"])
        elif self.args['print_table_stats']:
            print_covid_table_stats(conn, inspector, self.args['--table_name'])
        elif self.args['sign_up']:
            sign_up(conn,self.args['--username'], self.args['--password'])

def create_connection(username='postgres', password='mysecretpassword'):
    connection_string = 'postgresql://{0}:{1}@localhost:5432/sona460'.format(username, password)
    environ['SONA460_CONN_STR'] = connection_string
    return connection_string

def sign_up(conn,username, password):
    statement = """CREATE USER {0} WITH PASSWORD \'{1}\'""".format(username, password)
    conn.execute(statement)
    statement = """GRANT ALL ON coviddays TO {0}""".format(username)
    conn.execute(statement)
    print('Created user {0}'.format(username))
    
def load_from_csv(conn, engine, path='/Users/jacobgoldverg/covidata/csse_covid_19_daily_reports_us/05-21-2021.csv'):
    #load csv into pandas data frame
    df = pd.read_csv(path)
    df.fillna(0, inplace=True)
    df['Last_Update'] = pd.to_datetime(df['Last_Update'])
    df.columns= df.columns.str.strip().str.lower()
    name = "coviddays"
    try:
        df.to_sql('coviddays', engine, if_exists='append')
    except:
        data = pd.read_sql('SELECT * FROM coviddays', engine)
        df2 = pd.concat([data,df])
        df2.fillna(0, inplace=True)
        df2.to_sql(name='coviddays', con=engine, if_exists = 'replace')
    conn.close()

def drop_table_row(conn, table_name, pk):
    conn.execute(""" DELETE FROM coviddays WHERE """)

def drop_table(table_name, conn):
    conn.execute("""DROP table \""""+ table_name+"\"")

def make_covid_days_unique_constraint_and_primary_key(conn, insp):
    if not insp.get_unique_constraints('coviddays'):
        result = conn.execute(
            """ ALTER TABLE coviddays ADD CONSTRAINT uni_coviddays UNIQUE(uid, last_update);
            """
        )
        print("Created unique constraint called " + "uni_coviddays")
    if not insp.get_pk_constraint('coviddays'):
        result = conn.execute(
            """ ALTER TABLE coviddays ADD CONSTRAINT pk_coviddays PRIMARY KEY (uid, last_update);
            """
        )
        print("Created pk constraint called "+ "pk_coviddays")
    print("Executed make coviddays unique constraint and primary key creation by altering table")

def drop_column(table_name, column_name, conn):
    result = conn.execute("""ALTER TABLE \""""+ table_name+"\"" + " DROP COLUMN " + "\""+column_name + "\"")
    print_query_result(result)

def get_date(conn, year=0, month=0, day=0):
    statement = """ SELECT * FROM coviddays WHERE """
    boolWrittenToo = False
    if int(day) > 0:
        statement += """EXTRACT(day FROM \"last_update\") = {0}""".format(day)
        boolWrittenToo = True
    if int(month) > 0:
        if not boolWrittenToo:
            statement += """EXTRACT(month FROM \"last_update\") = {0} """.format(month)
            boolWrittenToo = True
        else:
            statement += """AND EXTRACT(month FROM \"last_update\") = {0}""".format(month)
    if int(year) > 0:
        if not boolWrittenToo:
            statement += """EXTRACT(year FROM \"last_update\") = {0}""".format(year)
            boolWrittenToo = True
        else:
            statement += """AND EXTRACT(year FROM \"last_update\") = {0}""".format(year)

    result = conn.execute(statement)
    print_query_result(result)

#gather the statistics about a table 
def print_stats(conn, state, column_name):
    statement = """select {1} from coviddays where coviddays.province_state=\'{0}\';""".format(state, column_name)
    result = conn.execute(statement)
    print_query_result(result, column_name)

def check_if_user_exists(conn, username):
    statement = """SELECT 1 FROM pg_roles WHERE rolname=\'{0}\'""".format(username)
    result = conn.execute(statement)
    re = result.first()[0]
    if re > 0:
        print('Login Worked')
        return True
    else:
        print('Login Failed')
        return False    
        
def print_covid_table_stats(conn, inspector, table_name='coviddays'):
    print("Columns:")
    pprint.pprint(inspector.get_columns(table_name))
    print('Keys: (oid, schemaname, relname, heap_blks_read, heap_blks_hit, heap_blks_icache_hit, idx_blks_read, idx_blks_hit, idx_blks_icache_hit, toast_blks_read, toast_blks_hit, toast_blks_icache_hit, tidx_blks_read, tidx_blks_hit, tidx_blks_icache_hit)')
    statement = """SELECT * FROM pg_statio_all_tables WHERE relname=\'{0}\';""".format(table_name)
    result = conn.execute(statement)
    for row in result:
        pprint.pprint(row)

def print_query_result(result, column_name=''):
    size = 0
    print(column_name)
    for row in result:
        size+=1
        print(row)
    if size == 0:
        print("Empty Result")

def build_db_conn(connection_str):
    conn_str = connection_str
    if len(conn_str) <= 2:
        conn_str = connection_str
    engine = create_engine(connection_str)
    conn = engine.connect()    
    inspector = inspect(engine)
    return engine, conn, inspector

if __name__ == "__main__":
    #connect to local db with the passwords in the connection string
    arguments = docopt(__doc__, version='Sona460 CLI')
    engine, conn, inspector = build_db_conn('postgresql://postgres:mysecretpassword@localhost:5432/sona460')
    sona460 = Sona460()
    sona460.get_options(conn, engine, inspector)
    conn.close        