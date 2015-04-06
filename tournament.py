#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    query = "delete from matches;"
    c.execute(query);
    db.commit()
    db.close()

def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    query = "delete from players;"
    c.execute(query);
    db.commit()
    db.close()

def countPlayers():
    """Returns the number of players currently registered."""
    db = connect()
    c = db.cursor()
    query = "select count(*) from players;"
    c.execute(query);
    num = c.fetchall()[0][0]
    db.close()
    return num

def getPlayerID(name):
    """Utility function for getting the id of a player given their name.

    Args:
      name: the player's full name (need not be unique).
    Returns:
      The integer ID of the player.
    """
    db = connect()
    c = db.cursor()
    query = "select id from players where name=%s;"
    c.execute(query,(name,));
    player_id = c.fetchall()
    db.close()

    return player_id[0][0]

def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    query = "insert into players (name) values (%s);"
    c.execute(query,(name,))
    db.commit()
    print "Player %s added" % name
    db.close()

def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    db = connect()
    c = db.cursor()
    query = """
            select id,name,count(m.winner) as wins,count(m.winner)+count(n.loser) as matches
                from players left join matches as m on id=m.winner 
                left join matches as n on id=n.loser 
                group by id order by wins desc,id;
            """
    c.execute(query)
    results = c.fetchall()
    db.close()

    return results

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()

    query = "insert into matches (winner,loser) values (%s,%s);"
    c.execute(query,(winner,loser,))
    db.commit()
    print "Match added: %s,%s" % (winner,loser)
    db.close()

def getByes():
    """Returns the ids of players who have had byes in the tournament.

    Returns:
      A list of player IDs.
    """
    db = connect()
    c = db.cursor()
    query = "select id from players join matches on id=winner where loser is NULL group by id having count(*) > 0;"
    c.execute(query)
    byes = c.fetchall()
    db.close()
    return [row[0] for row in byes]
 

def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # get the current standings, ordered by wins, then id to match playerStandings
    # include a byes column
    db = connect()
    c = db.cursor()
    query = """
            select id,name,count(winner) as wins,
                (select count(*) from matches where winner=id and loser is NULL) as byes 
                from players left join matches on id=winner 
                group by id order by wins desc,id;
            """
    c.execute(query)
    standings = c.fetchall()
    db.close()
    
    # If there are an uneven number of players, give the lowest-ranked one a bye
    # in the next round. Give it to the next-lowest player if the lowest already has 
    # a bye in this tournament.
    if len(standings)%2 != 0:
        bye_index = 0
        rev_standings = standings[::-1]
        for s in rev_standings:
            if s[3] == 0:
                bye_index = standings.index(s)
                break
        standings.insert(bye_index+1,(0,"Bye",0,0))

    
    # our list is ordered by wins, so just split it up into pairs and join
    # each pair into a single tuple
    pairs = [x[:2]+y[:2] for x,y in zip(standings[::2],standings[1::2])]
    return pairs
