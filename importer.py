import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import io
df = pd.read_csv('csse_covid_19_daily_reports_us/12-04-2020.csv')
df.columns = [c.lower() for c in df.columns] #postgres doesn't like capitals or spaces
print(df.columns)
engine = create_engine('postgresql://postgres:Jacob123@localhost:5432/coviddata')
conn = engine.raw_connection()
df.head(0).to_sql('coviddays', engine, if_exists='replace',index=False) #drops old table and creates new empty table
cur = conn.cursor()
output = io.StringIO()
df.to_csv(output, sep='\t', header=False, index=False)
output.seek(0)
contents = output.getvalue()
cur.copy_from(output, 'coviddays', null="") # null values become ''
conn.commit()
