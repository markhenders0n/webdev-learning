import pandas as pd
import pyodbc

# make connection to local server
conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};' 
                      'Server=localhost;'
                      'Database=master;'
                      'Trusted_Connection=yes;',
                      autocommit=True)

cursor= conn.cursor()

cursor.execute("CREATE DATABASE BlackJack") # create database for storing all blackjack cards and switch to new database
cursor.execute("USE BlackJack")

cursor.execute("CREATE TABLE Diamond(Type NVARCHAR(255), Value int);") # create tables for each suite of cards
cursor.execute("CREATE TABLE Heart(Type NVARCHAR(255), Value int);")
cursor.execute("CREATE TABLE Club(Type NVARCHAR(255), Value int);")
cursor.execute("CREATE TABLE Spade(Type NVARCHAR(255), Value int);")

cursor.execute("CREATE TABLE Deck(Type NVARCHAR(255), Value int)") # create tables for the shuffled deck and dealt hands
cursor.execute("CREATE TABLE Player(Type NVARCHAR(255), Value int)")
cursor.execute("CREATE TABLE Opponent(Type NVARCHAR(255), Value int)")

# create cards in each suite table
for i in range(10):
    cursor.execute("""INSERT INTO Diamond 
                      VALUES ('Diamond', %d);""" %(i+1))
    cursor.execute("""INSERT INTO Heart 
                      VALUES ('Heart', %d);""" %(i+1))
    cursor.execute("""INSERT INTO Club 
                      VALUES ('Club', %d);""" %(i+1))
    cursor.execute("""INSERT INTO Spade 
                      VALUES ('Spade', %d);""" %(i+1))

sql_query = pd.read_sql_query('SELECT * FROM BlackJack.dbo.Diamond', conn) # check to make sure data is created properly
print(sql_query)
sql_query = pd.read_sql_query('SELECT * FROM BlackJack.dbo.Heart', conn)
print(sql_query)
sql_query = pd.read_sql_query('SELECT * FROM BlackJack.dbo.Club', conn)
print(sql_query)
sql_query = pd.read_sql_query('SELECT * FROM BlackJack.dbo.Spade', conn)
print(sql_query)

cursor.execute("""
                    USE master;
                    ALTER DATABASE BlackJack SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                    DROP DATABASE BlackJack;
               """) # delete database after game

