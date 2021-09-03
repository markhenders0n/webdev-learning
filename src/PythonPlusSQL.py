import pandas as pd
import pyodbc
conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};'
                      'Server=localhost;'
                      'Database=Family;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()

sql_query = pd.read_sql_query('SELECT * FROM Family.dbo.Parents', conn)
print(sql_query)
print(type(sql_query))

cursor.execute('SELECT * FROM Family.dbo.Cousins')

for row in cursor:
    print(row)