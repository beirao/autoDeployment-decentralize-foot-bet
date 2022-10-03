from brownie import Bet, network, config, Contract, accounts, Wei
import sys
import sqlite3 as db
import yaml, json
import logging

with open("ext/config-bet.yaml", "r") as stream:
    try:
        config_bet = yaml.safe_load(stream)
    except yaml.YAMLError as e:
        print(e)
        logging.error(f"Error yaml : {e}")

logging.basicConfig(filename=config_bet["logPath"], level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s")

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

def saveAddrDb(contractAddress, matchId) :
    try :
        connection = db.connect(config_bet["databasePath"])
        cursor = connection.cursor()
        req = f"UPDATE matches SET address = '{str(contractAddress)}' WHERE match_id = {matchId}"
        cursor.execute(req)

        # update data base at isDeployed = 1            
        req = f"UPDATE matches SET isDeployed = 1 WHERE match_id = {matchId}"
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
        account = accounts.add(config["wallets"]["from_key"])
        print("account : ", account)

        # Vars :
        jobId = bytes(config["networks"][network.show_active()]["jobId"],'utf-8')
        oracle = config["networks"][network.show_active()]["oracle"]
        requestFee = config["networks"][network.show_active()]["requestFee"]
        linkTokenAddress = config["networks"][network.show_active()]["linkToken"]
        timeout = config["networks"][network.show_active()]["timeout"]
        apiUrl = config["networks"][network.show_active()]["apiUrl"]

        args = [matchId, matchTimestamp, timeout, oracle, apiUrl, jobId, requestFee, linkTokenAddress]
        print(args)
        bet = Bet.deploy(
            matchId, 
            matchTimestamp, 
            timeout,
            oracle, 
            apiUrl,
            jobId, 
            requestFee, 
            linkTokenAddress,
            {"from": account},
            publish_source=config["networks"][network.show_active()].get("verify", False)   
        )
        print("Deployed !")

        print("Fund contract with LINK...")
        linkTokenAbi = json.load(open("abi/linkTokenAbi.json"))
        LinkTokenAddr = config["networks"][network.show_active()]["linkToken"]
        linkToken = Contract.from_abi("linkToken", LinkTokenAddr, linkTokenAbi)
        tx = linkToken.transfer(bet.address, config["networks"][network.show_active()]["fundAmount"], {"from": account})
        tx.wait(1)
        print("Fund link contract!")
        logging.info(f"Deployed at : {bet.address}")

        saveAddrDb(bet.address, matchId)

    except Exception as e :
        print("Error deployBet  :",e,file=sys.stderr)
        logging.error(f"Error deployBet : {e}")

# test cmd : brownie run scripts/deploy.py deployBet 23 675763876768 --network goerli








