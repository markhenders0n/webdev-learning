import pandas as pd
import pyodbc
import random as rm

# function used for passing shuffle command to SQL
def shuffleCard(allIterator, suiteIterator, suiteName):
    if(suiteIterator == 10):
        cardNum = 1
    elif(suiteIterator > 10):
        allIterator -= 1
        return(allIterator)
    else:
        cardNum = rm.randrange(1, 11-suiteIterator, 1)
    query = """
                INSERT INTO Deck (RowID, Type, Value)
                SELECT RowID,Type,Value FROM %s
                WHERE RowID=%d;

                UPDATE Deck
                SET RowID=%d
                WHERE RowID=%d;

                DELETE FROM %s
                WHERE RowID=%d;

                UPDATE %s
                SET RowID-=1
                WHERE RowID>%d;
            """ % (suiteName, cardNum, allIterator, cardNum, suiteName, cardNum, suiteName, cardNum)
    cursor.execute(query)
    return(allIterator)

# make connection to local server
conn = pyodbc.connect('Driver={SQL Server Native Client 11.0};' 
                      'Server=localhost;'
                      'Database=master;'
                      'Trusted_Connection=yes;',
                      autocommit=True)

cursor= conn.cursor()

cursor.execute("CREATE DATABASE BlackJack") # create database for storing all blackjack cards and switch to new database
cursor.execute("USE BlackJack")

cursor.execute("CREATE TABLE Diamond(RowID int, Type NVARCHAR(255), Value int);") # create tables for each suite of cards
cursor.execute("CREATE TABLE Heart(RowID int, Type NVARCHAR(255), Value int);")
cursor.execute("CREATE TABLE Club(RowID int, Type NVARCHAR(255), Value int);")
cursor.execute("CREATE TABLE Spade(RowID int, Type NVARCHAR(255), Value int);")

cursor.execute("CREATE TABLE Deck(RowID int NOT NULL, Type NVARCHAR(255), Value int)") # create tables for the shuffled deck and dealt hands
cursor.execute("CREATE TABLE Player(RowID int IDENTITY(1,1), Type NVARCHAR(255), Value int)")
cursor.execute("CREATE TABLE Opponent(RowID int IDENTITY(1,1), Type NVARCHAR(255), Value int)")

# create cards in each suite table
for i in range(10):
    cursor.execute("""INSERT INTO Diamond 
                      VALUES (%d, 'Diamond', %d);""" %(i+1, i+1))
    cursor.execute("""INSERT INTO Heart 
                      VALUES (%d, 'Heart', %d);""" %(i+1, i+1))
    cursor.execute("""INSERT INTO Club 
                      VALUES (%d, 'Club', %d);""" %(i+1, i+1))
    cursor.execute("""INSERT INTO Spade 
                      VALUES (%d, 'Spade', %d);""" %(i+1, i+1))

sql_query = pd.read_sql_query('SELECT * FROM BlackJack.dbo.Diamond', conn) # check to make sure data is created properly
print(sql_query)
sql_query = pd.read_sql_query('SELECT * FROM BlackJack.dbo.Heart', conn)
print(sql_query)
sql_query = pd.read_sql_query('SELECT * FROM BlackJack.dbo.Club', conn)
print(sql_query)
sql_query = pd.read_sql_query('SELECT * FROM BlackJack.dbo.Spade', conn)
print(sql_query)

d = 1
h = 1
c = 1
s = 1
i = 1

# issue where RowID doesn't update after card entry is deleted

while i < 41:
    
    suiteNum = rm.randrange(0, 4, 1)
    if(suiteNum == 0):
        # Shuffle card from Diamond Suite
        i = shuffleCard(i, d, "Diamond")
        d += 1

    elif(suiteNum == 1):
        # Shuffle card from Heart Suite
        i = shuffleCard(i, h, "Heart")
        h += 1

    elif(suiteNum == 2):
        # Shuffle card from Club Suite
        i = shuffleCard(i, c, "Club")
        c += 1

    else:
        # Shuffle card from Spade Suite
        i = shuffleCard(i, s, "Spade")
        s += 1
    
    i += 1

# clean up after game
# cursor.execute("""
#                     USE master;
#                     ALTER DATABASE BlackJack SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
#                     DROP DATABASE BlackJack;
#                """) # delete database after game