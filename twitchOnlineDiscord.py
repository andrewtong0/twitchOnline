import discord
import asyncio
import requests  # Sends requests to the New Twitch API
import re  # Regular expressions for parsing through data
from urllib.request import urlopen

client = discord.Client()
# List of streams to check online status of
# Recommended to put all names in full lowercase since Twitch seems to handle capitalization incorrectly
users = ['STREAMER LIST GOES HERE']
# Client ID (for authentication with Twitch API)
headers = {'Client-ID': 'TWITCH CLIENT ID HERE',}

global channel
channel = discord.Object(id='DISCORD CHANNEL ID HERE')

async def my_background_task():
    titleDict = {}  # Array used to store the titles of each stream
    titleSuffix = 0;
    global uptimeDict
    uptimeDict = {}
    usersDict = {}  # Dictionary storing streamer + status (offline on runtime)

    # Set status of all streamers to offline
    for x in users:
        usersDict.update({x: "offline"})

    # Declaration of arrays
    online = []  # Array used for .online command for currently online streams

    await client.wait_until_ready()
    while not client.is_closed:
        params = []  # Reset parameters on each loop
        for x in users:
            params.append(('user_login', x))
        # Sending headers + parameters to the Twitch API to return information
        response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params)

        # Creating a dictionary with streamer names + their stream titles
        numOnline = (response.text.count('title":"'))
        while (numOnline > 0):
            titlePrefix = (response.text.find('title":"', titleSuffix)) + 8
            titleSuffix = (response.text.find('","viewer', titlePrefix))
            streamTitle = (response.text[titlePrefix:titleSuffix])

            namePrefix = (response.text.find('live_user_', titleSuffix)) + 10
            nameSuffix = (response.text.find('-{width', namePrefix))
            streamerName = (response.text[namePrefix:nameSuffix])

            uptimePrefix = (response.text.find('"started_at":"', titleSuffix)) + 14
            uptimeSuffix = (response.text.find('","language', uptimePrefix))
            uptimeDict[streamerName] = (response.text[uptimePrefix:uptimeSuffix])

            titleDict[streamerName] = streamTitle

            numOnline -= 1

        # Discord Notifications
        for x in users:  # Update associated dictionary entries with online status when online
            if re.search(x, response.text, 0) != None and usersDict[x] == "offline":
                usersDict[x] = "online"
                # Only drop a message in the updates once after a stream goes online
                await client.send_message(channel, "**" + str(x) + "** is now streaming: **" + titleDict[x] + "**" + """
    """ + " <https://www.twitch.tv/" + str(x) + ">")
                print(str(x) + " just went live")
            if usersDict[x] == "online":
                online.append(x)
            if re.search(x, response.text, 0) == None and usersDict[x] == "online":
                usersDict[x] = "offline"
                titleDict[x] = ""
                print(str(x) + " has gone offline")
        online = []  # Clear the list of online streamers so they don't exponentially stack (refreshed on each loop)
        await asyncio.sleep(10)  # task runs every 60 seconds


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

    if message.content.startswith('!uptime'):
        await client.wait_until_ready()
        userReq = message.content.partition("!uptime ")[2]
        if userReq in uptimeDict:
            await client.send_message(message.channel, "**" + userReq + "** has been streaming since: **" + str(
                uptimeDict[userReq]) + "** (PST is -8h)")
        else:
            await client.send_message(message.channel, "User could not be found or is currently offline.")


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.loop.create_task(my_background_task())
client.run('DISCORD CLIENT TOKEN HERE')
