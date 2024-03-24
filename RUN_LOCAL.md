# Running the bot locally
### PREREQUISITES
- Mongodb database access
- Discord bot token
- Riot API key

### Steps
- Insert all values from above into a new .env file. Template for such file can be found in `env_example` file in the root.
  - `riotApiKey = <Riot games API key>`
  - `botToken = <Discord bot token>`
  - `mongodb = "Docker"` (for local docker container in same network)
    - also set `dockerContainer = <conatainer name>` and `mongoUsername` & `mongoPassword`
  - or `mongodb = "External"` (for externally hosted mongodb)
    - also set `MongodbConnectionString = <connection string to external database>`
  - or `mongodb = ""` (for mongodb accessible through localhost:27017)
    - alse set `mongoUsername` & `mongoPassword`
- Ideally create a venv from the root folder and activate it `python3 -m venv venv && source ./venv/bin/activate`
- Install all requirements `python3 -m pip install -r requirements.txt`
- Run the bot `python3 -m mundobot`
                                                     
