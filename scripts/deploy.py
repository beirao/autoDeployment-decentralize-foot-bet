from datetime import datetime
from brownie import Bet, network, config, Contract, accounts
import sys
import sqlite3 as db
import yaml
import logging

with open("config-bet.yaml", "r") as stream:
    try:
        config_bet = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        print(e)
        logging.error(f"Error yaml : {e}")

logging.basicConfig(filename=config_bet["logPath"], level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s")

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])

def saveAddrDb(contractAddress, matchId) :
    try :
        connection = db.connect(config_bet["databasePath"])
        cursor = connection.cursor()
        req = f"UPDATE match SET address = '{str(contractAddress)}' WHERE match_id = {matchId}"
        cursor.execute(req)

        # update data base at isDeployed = 1            
        req = f"UPDATE match SET isDeployed = 1 WHERE match_id = {matchId}"
        cursor.execute(req)
        connection.commit();    

        print("DB updated")
        
    except Exception as e :
        print("Error saveAddrDb :",e)
        logging.error(f"Error saveAddrDb : {e}")


    finally :
        connection.close()

    
# cmd  :  brownie run scripts/deploy.py deployBet matchId matchTimestamp --network goerli
def deployBet(matchId, matchTimestamp):
    try :
        account = get_account()

        # Vars :
        jobId = config["networks"][network.show_active()]["jobId"]
        oracle = config["networks"][network.show_active()]["oracle"]
        fee = config["networks"][network.show_active()]["fee"],
        linkTokenAddress = config["networks"][network.show_active()]["linkToken"]

        bet = Bet.deploy(
            matchId, 
            matchTimestamp, 
            oracle, 
            jobId, 
            str(fee[0]), 
            linkTokenAddress,
            {"from": account},
            publish_source=config["networks"][network.show_active()].get("verify", False)
        )
        print("Deployed !")

        print("Fund contract with LINK...")
        LinkTokenAddr = config["networks"][network.show_active()]["linkToken"]
        LinkToken = Contract.from_explorer(LinkTokenAddr)
        tx = LinkToken.transfer(bet.address, config["linkFundAmount"], {"from": account})
        tx.wait(1)
        print("Fund link contract!")
        logging.info(f"Deployed at : {bet.address}")

        saveAddrDb(bet.address, matchId)

    except Exception as e :
        print("Error deployBet  :",e,file=sys.stderr)
        logging.error(f"Error deployBet : {e}")








