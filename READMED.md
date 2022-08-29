# AutoDeployment_DecentralizedFootBet

```bash
brownie run scripts/deploy.py deployBet matchId matchTimestamp --network goerli
```

# cmd : Cron every 12 hours

```bash
brownie run scripts/main.py
```

## SQL Create table match

```sql
CREATE TABLE "match" (
    "match_id" INTEGER UNIQUE,
    "date" INTEGER,
    "status" TEXT,
    "league_id" INTEGER,
    "league_string" TEXT,
    "home_id" INTEGER NOT NULL,
    "home_string" TEXT NOT NULL,
    "home_logo" TEXT,
    "away_id" INTEGER NOT NULL,
    "away_string" TEXT NOT NULL,
    "away_logo" TEXT,
    "isDeployed" INTEGER,
    "address" TEXT,
    PRIMARY KEY("match_id")
);
```

git remote add origin https://github.com/beirao/centralize-backend-decentralize-foot-bet.git
git branch -M main
git push -u origin main
