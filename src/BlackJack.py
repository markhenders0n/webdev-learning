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
                SELECT %d,Type,Value FROM %s
                WHERE RowID=%d;

                DELETE FROM %s
                WHERE RowID=%d;

                UPDATE %s
                SET RowID-=1
                WHERE RowID>%d;
            """ % (allIterator, suiteName, cardNum, suiteName, cardNum, suiteName, cardNum)
    cursor.execute(query)
    return(allIterator)

def dealCard(participant, numUsed):
    cardNum = rm.randrange(1, 41-numUsed, 1)
    query = """
            INSERT INTO %s (Type, Value)
            SELECT Type,Value FROM Deck
            WHERE RowID=%d;

            DELETE FROM Deck
            WHERE RowID=%d;

            UPDATE Deck
            SET RowID-=1
            WHERE RowID>%d;
        """ % (participant, cardNum, cardNum, cardNum)
    cursor.execute(query)

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
        i = shuffleCard(i, d, 'Diamond')
        d += 1

    elif(suiteNum == 1):
        # Shuffle card from Heart Suite
        i = shuffleCard(i, h, 'Heart')
        h += 1

    elif(suiteNum == 2):
        # Shuffle card from Club Suite
        i = shuffleCard(i, c, 'Club')
        c += 1

    else:
        # Shuffle card from Spade Suite
        i = shuffleCard(i, s, 'Spade')
        s += 1
    
    i += 1

# deal two cards to player and opponent from deck table
numUsed = 0

for i in range(1,3):
    dealCard('Player', numUsed)
    numUsed += 1

for i in range(1,3):
    dealCard('Opponent', numUsed)
    numUsed += 1

cursor.execute("SELECT * FROM Player;")
playerCards = [cursor.fetchone(), cursor.fetchone()]
print("Your cards are %d of %ss and %d of %ss" % (playerCards[0].Value, playerCards[0].Type,
                                                playerCards[1].Value, playerCards[1].Type))

cursor.execute("SELECT * FROM Opponent;")
opponentCards = [cursor.fetchone(), cursor.fetchone()]
print("Your opponents cards are %d of %ss and %d of %ss" % (opponentCards[0].Value, opponentCards[0].Type,
                                                            opponentCards[1].Value, opponentCards[1].Type))

# ask user if they want more cards. call draw function when answered with y. end game otherwise
answer = "y"
while(answer != "n"):
    playerTotal = 0
    opponentTotal = 0
    answer = input("Would you like to draw another card? (y/n)")
    if(answer is "y"):
        dealCard('Player', numUsed)
        numUsed += 1
        cursor.execute("SELECT * FROM Player WHERE RowID>%d;" %(len(playerCards)))
        playerCards.append(cursor.fetchone())
        print("You drew a %d of %ss" % (playerCards[-1].Value, playerCards[-1].Type))
        
        dealCard('Opponent', numUsed)
        numUsed += 1
        cursor.execute("SELECT * FROM Opponent WHERE RowID>%d;" %(len(opponentCards)))
        opponentCards.append(cursor.fetchone())
        print("Your opponent drew a %d of %ss" % (opponentCards[-1].Value, opponentCards[-1].Type))

    for i in range(len(playerCards)):
        playerTotal += playerCards[i].Value
    if(playerTotal > 21):
        answer = "n"
        print("Bust, you lose...")
        continue

    for i in range(len(opponentCards)):
        opponentTotal += opponentCards[i].Value
    if(opponentTotal > 21):
        answer = "n"
        print("Opponent bust, you win!")
        continue

# decide game's outcome and notify player
if(playerTotal < 21 and opponentTotal < 21):
    totalDifference = playerTotal - opponentTotal
    if(totalDifference > 0):
        print("You were closest to 21 so you win!")
    elif(totalDifference < 0):
        print("The opponent was closer to 21 so you lose...")
    else:
        print("It's a tie!")

# clean up after game
cursor.execute("""
                    USE master;
                    ALTER DATABASE BlackJack SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
                    DROP DATABASE BlackJack;
               """) # delete database after game