import schedule
import os
import time
import yaml
import logging

def job() :
    logging.info("--------------------------------------- RUN UPDATE ---------------------------------------")
    print("Called...")
    os.system("brownie run scripts/main.py")
    

if __name__ == "__main__":

    with open("ext/config-bet.yaml", "r") as stream:
        try:
            config_bet = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    logging.basicConfig(filename=config_bet["logPath"], level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s")

    # schedule.every(2).seconds.do(job)
    schedule.every(config_bet["deltaTimedeploymentUpdate"]).hours.do(job)

    job() # exec job once at the beginning
    while 1:
        try :
            schedule.run_pending()
        except Exception as e :
            print("Error cron :",e)
        finally :
            # time.sleep(60)
            time.sleep(2)
