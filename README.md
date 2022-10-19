# AutoDeployment_DecentralizedFootBet

## Deploy one contract bet

This code auto deployment bet contracts for the [Decentralize-foot-bet](https://github.com/beirao/main-decentralize-foot-bet) project using the [football-data.org](https://www.football-data.org/) API.

```bash
brownie run scripts/deploy.py deployBet matchId matchTimestamp --network goerli
```

## Cron every x hours

You can setup the time interval in "ext/config-bet.yaml".

```bash
brownie run scripts/main.py
```

## SQL Create table match

```sql
CREATE TABLE IF NOT EXISTS matches
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
                            PRIMARY KEY("match_id"));
```

# Docker

## Build

```bash
sudo docker build -t auto-deploy-boarbet .
```

## Run image

```bash
sudo docker run -v dst:/main/ext auto-deploy-boarbet
```

## Save the image

```bash
sudo docker save -o auto-deploy-boarbet.tar auto-deploy-boarbet
```
