from datetime import datetime
from nis import match
import sqlite3 as db
import numpy as np
import sys
sys.path.insert(0, './scripts')
from request import requestMatchPlanning
import yaml
import subprocess
import logging

with open("ext/config-bet.yaml", "r") as stream:
    try:
        config_bet = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        print(e)
        logging.error(f"Error yaml : {e}")

logging.basicConfig(filename=config_bet["logPath"], level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s")


def dataBaseUpdate(rmpArray, connection, cursor) :
    for match_api in rmpArray :
        match_data = cursor.execute('SELECT * FROM matches WHERE match_id = ?', (match_api[0],)).fetchone()

        if(match_data == None and (match_api[2] == "SCHEDULED" or match_api[2] == "TIMED")) :
            req = f"INSERT INTO matches VALUES {tuple(match_api)};"
            cursor.execute(req)
            print("DB updated, matches ID: ", match_api[0])
            logging.info(f"DB updated, matches ID : {match_api[0]}")
    
    connection.commit()

def deployContract(connection, cursor) :
    allmatchesUpToDate = True
    # look at undeployed contract
    req = cursor.execute('SELECT * FROM matches WHERE isDeployed = ?', (0,))
    deployementNeeded  = req.fetchall()

    # deploy contracts
    for i in deployementNeeded :
        if (    i[4] in config_bet["listBetLeague"] 
            and (i[2] == "SCHEDULED" or i[2] == "TIMED") 
            and (datetime.timestamp(datetime.now()) < i[1] - (config_bet["minimumTimeBeforeDeployment"])*60*60*24)) :
 
            try :
                allmatchesUpToDate = False
                print(f"Deploying : matches ID {i[0]} league {i[4]}")
                logging.info(f"Deploying : matches ID {i[0]} league {i[4]} - {i[6]} VS {i[10]}")
                process = subprocess.run(["brownie","run","scripts/deploy.py","deployBet", str(i[0]), str(i[1]), "--network", "goerli"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if(process.stderr != "") :
                    raise Exception(process.stderr)

            except Exception as e :
                print("Error deployContract :",e)
                logging.error(f"Error deployContract : {e}")

            connection.commit()

    if allmatchesUpToDate :
        print("All matches were up-to-date")
        logging.info("All matches were up-to-date")

    else :
        print("All deployed")
        logging.info("All deployed")

    connection.commit()

# rmpArray element : 
# (417226, '1600383893', 'TIMED', 2015, 'Ligue 1', 
# 511, 'Toulouse FC', 'https://crests.football-data.org/511.png', 
# 524, 'Paris Saint-Germain FC', 'https://crests.football-data.org/524.png', 
# 0, '0x')]
def main() :
    try : 
        connection = db.connect(config_bet["databasePath"])
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS matches
                        ("match_id" INTEGER UNIQUE,
                            "date" INTEGER,
                            "status" TEXT,
                            "league_id" INTEGER,
                            "league_string" TEXT,
                            "home_id" INTEGER NOT NULL,
                            "home_string" TEXT NOT NULL,
                            "home_logo" TEXT,
                            "home_score" INTEGER,
                            "away_id" INTEGER NOT NULL,
                            "away_string" TEXT NOT NULL,
                            "away_logo" TEXT,
                            "away_score" INTEGER,
                            "isDeployed" INTEGER,
                            "address" TEXT,
                            PRIMARY KEY("match_id"))''')
        connection.commit()
        rmpArray = np.array(requestMatchPlanning())
        dataBaseUpdate(rmpArray, connection, cursor)
        deployContract(connection, cursor)

    except Exception as e :
        print("Error main :",e)
        logging.error(f"Error main : {e}")

    finally :
        connection.close()


if __name__ == "__main__":
    # connection = db.connect(config_bet["databasePath"])
    # cursor = connection.cursor()
    # cursor.execute('IF EXISTS(DELETE FROM match)')
    # connection.commit();    
    # connection.close()

    main()