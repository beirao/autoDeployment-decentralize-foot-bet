from asyncio import FastChildWatcher
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

with open("config-bet.yaml", "r") as stream:
    try:
        config_bet = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        print(e)
        logging.error(f"Error yaml : {e}")

logging.basicConfig(filename=config_bet["logPath"], level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s")


def dataBaseUpdate(rmpArray, connection, cursor) :
    for match_api in rmpArray :
        match_data = cursor.execute('SELECT * FROM match WHERE match_id = ?', (match_api[0],)).fetchone()

        if(match_data == None and (match_api[2] == "SCHEDULED" or match_api[2] == "TIMED")) :
            req = f"INSERT INTO match VALUES {tuple(match_api)};"
            cursor.execute(req)
            print("DB updated, match ID: ", match_api[0])
            logging.info(f"DB updated, match ID : {match_api[0]}")
    
    connection.commit()

def deployContract(connection, cursor) :
    allMatchsUpToDate = True
    # look at undeployed contract
    req = cursor.execute('SELECT * FROM match WHERE isDeployed = ?', (0,))
    deployementNeeded  = req.fetchall()

    # deploy contracts
    for i in deployementNeeded :
        if (    i[4] in config_bet["listBetLeague"] 
            and (i[2] == "SCHEDULED" or i[2] == "TIMED") 
            and (datetime.timestamp(datetime.now()) < i[1] - (config_bet["minimumTimeBeforeDeployment"])*60*60*24)) :
 
            try :
                allMatchsUpToDate = False
                print(f"Deploying : match ID {i[0]} league {i[4]}")
                logging.info(f"Deploying : match ID {i[0]} league {i[4]}")
                process = subprocess.run(["brownie","run","scripts/deploy.py","deployBet", str(i[0]), str(i[1]), "--network", "goerli"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if(process.stderr != "") :
                    raise Exception(process.stderr)

            except Exception as e :
                print("Error deployContract :",e)
                logging.error(f"Error deployContract : {e}")


    connection.commit()
    if allMatchsUpToDate :
        print("All matches were up-to-date")
        logging.info("All matches were up-to-date")

    else :
        print("All deployed")
        logging.info("All deployed")





# rmpArray element : 
# (417226, '1600383893', 'TIMED', 2015, 'Ligue 1', 
# 511, 'Toulouse FC', 'https://crests.football-data.org/511.png', 
# 524, 'Paris Saint-Germain FC', 'https://crests.football-data.org/524.png', 
# 0)]
def main() :
    try : 
        # logging.basicConfig(filename=config_bet["logPath"], level=logging.INFO,
        #             format="%(asctime)s %(levelname)s %(message)s")
        connection = db.connect(config_bet["databasePath"])
        cursor = connection.cursor()
        rmpArray = np.array(requestMatchPlanning())
        dataBaseUpdate(rmpArray, connection, cursor)
        deployContract(connection, cursor)

    except Exception as e :
        print("Error main :",e)
        logging.error(f"Error main : {e}")

    finally :
        connection.close()


if __name__ == "__main__":
    connection = db.connect(config_bet["databasePath"])
    cursor = connection.cursor()
    cursor.execute('DELETE FROM match')
    connection.commit();    
    connection.close()

    main()