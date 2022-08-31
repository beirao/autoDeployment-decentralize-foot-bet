import schedule
import os
import time
import yaml


with open("config-bet.yaml", "r") as stream:
    try:
        config_bet = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)


def job() :
    print("Called...")
    os.system("brownie run scripts/main.py")
    #os.system("ls")
    

schedule.every(config_bet["deltaTimedeploymentUpdate"]).hour.do(job)


while 1:
    try :
        schedule.run_pending()
    except Exception as e :
        print("Error cron :",e)
    finally :
        time.sleep(60)
