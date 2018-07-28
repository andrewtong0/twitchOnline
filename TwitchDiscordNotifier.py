import discord
import asyncio
import requests # Sends requests to the New Twitch API
import re # Regular expressions for parsing through data

client = discord.Client()
# List of streams to check online status of
# Recommended to put all names in full lowercase since Twitch seems to handle capitalization incorrectly
users = ['LIST OF STREAMERS TO CHECK HERE']

# Client ID (for authentication with Twitch API)
headers = {'Client-ID': 'TWITCH CLIENT ID', }

async def my_background_task():

    usersDict = {}  # Dictionary storing streamer + status (offline on runtime)

    # Set status of all streamers to offline
    for x in users:
        usersDict.update({x: "offline"})

    # Declaration of arrays
    online = []  # Array used for .online command for currently online streams

    await client.wait_until_ready()
    channel = discord.Object(id='DISCORD CHANNEL ID HERE AND IN SECOND FUNCTION')
    while not client.is_closed:
        params = []  # Reset parameters on each loop
        for x in users:
            params.append(('user_login', x))
        # Sending headers + parameters to the Twitch API to return information
        response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params)

        # SLACK NOTIFICATIONS
        for x in users:  # Update associated dictionary entries with online status when online
            if re.search(x, response.text, 0) != None and usersDict[x] == "offline":
                usersDict[x] = "online"
                # Only drop a message in the updates once after a stream goes online
                await client.send_message(channel, str(x) + " is now streaming: <https://www.twitch.tv/" + str(x) + ">")
                print(str(x) + " just went live")
            if usersDict[x] == "online":
                online.append(x)
            if re.search(x, response.text, 0) == None and usersDict[x] == "online":
                usersDict[x] = "offline"
                print(str(x) + " has gone offline")
        online = []  # Clear the list of online streamers so they don't exponentially stack (refreshed on each loop)
        await asyncio.sleep(10) # task runs every 60 seconds

@client.event
async def on_message(message):
    if message.content.startswith('!online'):
        usersDict = {}  # Dictionary storing streamer + status (offline on runtime)

        # Set status of all streamers to offline
        for x in users:
            usersDict.update({x: "offline"})

        # Declaration of arrays
        online = []  # Array used for .online command for currently online streams

        await client.wait_until_ready()
        channel = discord.Object(id='DISCORD CHANNEL ID HERE AND FIRST FUNCTION')
        params = []  # Reset parameters on each loop
        for x in users:
            params.append(('user_login', x))
        # Sending headers + parameters to the Twitch API to return information
        response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params)

        # SLACK NOTIFICATIONS
        for x in users:  # Update associated dictionary entries with online status when online
            if re.search(x, response.text, 0) != None and usersDict[x] == "offline":
                usersDict[x] = "online"
            if usersDict[x] == "online":
                online.append(x)
            if re.search(x, response.text, 0) == None and usersDict[x] == "online":
                usersDict[x] = "offline"
        onlinelist = re.sub("'", '', str(online), 0, 0)
        await client.send_message(message.channel, "Currently online: " + str(onlinelist))
        online = []  # Clear the list of online streamers so they don't exponentially stack (refreshed on each loop)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.loop.create_task(my_background_task())
client.run('DISCORD TOKEN')
