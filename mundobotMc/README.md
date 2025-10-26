# Mundobot MC
Simplified version of the discord bot. Used to announce players that logged in to a Minecraft server.

## Run locally
It is required to have python3 installed as well as requirements from ```/requirements.txt```.  
Next step is setting up .env file - required fields are
- ```botToken```: Discord bot API key
- ```mcAnnouncementsDiscordChannelName```: Name of the channel that should receive the announcements. No need to set specific guild as the bot will send announcement to all guilds it is registered in.
- ```logFilePath```: Path to the latest.log file of the Minecraft server.

## Run in a docker
First build or pull ```mundobot-mc``` docker image.  
Then you need to either: 
1. create .env file with just ```botToken``` and ```mcAnnouncementsDiscordChannelName``` variables and mount it in the root directory of the container using ``````
2. or create env file locally and pass it in using ```--env-file <envfile/path>``` option.
You also need to mount the log file using ``````.  
Last step is running the docker image. For convenience a ```docker-compose-mc.yml``` file will be provided in the future.