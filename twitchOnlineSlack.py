import requests # Sends requests to the New Twitch API
import re # Regular expressions for parsing through data
from slackclient import SlackClient # Slack notification integration
import time # To control number of calls made

# TWITCH ONLINE NOTIFIER: Created by Andrew Tong

# The variables that need to be updated are the users variable (which streams to check),
# authentication variables (Slack + Twitch Client ID), and the slack channel to send updates to

# NOTES:
# .status command is case sensitive for usernames
# Max 100 names to check for

# Delay between subsequent passes (checks for commands/pulling stream info)
delay = 3 # In seconds

# List of streams to check online status of
# Recommended to put all names in full lowercase since Twitch seems to handle capitalization incorrectly
users = ['STREAMER LIST GOES HERE']
usersDict = {} # Dictionary storing streamer + status (offline on runtime)

# Set status of all streamers to offline
for x in users:
    usersDict.update({x: "offline"})

# Client ID (for authentication with Twitch API)
headers = {'Client-ID': 'TWITCH CLIENT ID GOES HERE',}

# Slack integration
token = 'xoxp-371964243174-370528179361-393787813828-bcff83cc40e5a654a576f15e616115ca'
sc = SlackClient(token)
channel = "stream-updates" # Slack channel name to send message

# Variable Declaration
online = [] # Array used for .online command for currently online streams
titleDict = {} # Array used to store the titles of each stream

counter = 2;
titleSuffix = 0;

# Infinite loop to continuously check stream status until termination
if sc.rtm_connect(): # Ensure Slack has successfully connected
    while True:
        # GETTING TWITCH API INFORMATION
        # Parameters to check with Twitch API
        params = []  # Reset parameters on each loop
        for x in users:
            params.append(('user_login', x))
        # Sending headers + parameters to the Twitch API to return information
        response = requests.get('https://api.twitch.tv/helix/streams', headers=headers, params=params)
        numOnline = (response.text.count('title":"'))
        while(numOnline > 0):
            titlePrefix = (response.text.find('title":"', titleSuffix)) + 8
            titleSuffix = (response.text.find('","viewer', titlePrefix))

            namePrefix = (response.text.find('live_user_', titleSuffix)) + 10
            nameSuffix = (response.text.find('-{width', namePrefix))
            numOnline -= 1
            streamTitle = (response.text[titlePrefix:titleSuffix])
            streamerName = (response.text[namePrefix:nameSuffix])
            titleDict[streamerName] = streamTitle

        # SLACK NOTIFICATIONS
        for x in users: # Update associated dictionary entries with online status when online
            if re.search(x, response.text, 0) != None and usersDict[x] == "offline":
                usersDict[x] = "online"
                # Only drop a message in the updates once after a stream goes online
                sc.api_call('chat.postMessage', channel=channel, text=str(x) + " is now streaming: " + titleDict[x] + " [www.twitch.tv/" + str(x) + "]",
                            username='Stream Notification Bot', icon_emoji=':robot_face:')
                print(x + " is now streaming: " + titleDict[x])


            if usersDict[x] == "online":
                online.append(x)
            if re.search(x, response.text, 0) == None and usersDict[x] == "online":
                usersDict[x] = "offline"
                titleDict[x] = ""
                print(str(x) + " has gone offline")
        events = sc.rtm_read() # Read through all events
        for event in events: # Iterate through all events that happen on the Slack channel
            if ('channel' in event and 'text' in event and event.get('type') == 'message'):
                text = event['text'] # Check text messages
                if '.online' in text.lower():
                    onlinelist = re.sub("'", '', str(online), 0, 0)
                    sc.api_call('chat.postMessage', channel=channel,
                                text="Streamers currently online: " + str(onlinelist),
                                username='Stream Notification Bot', icon_emoji=':robot_face:')
                if '.streams' in text.lower():
                    usersList = re.sub("'", '', str(users), 0, 0) # Clean up list of users being checked
                    sc.api_call('chat.postMessage', channel=channel,
                                text="Checking status of these streamers: " + str(usersList),
                                username='Stream Notification Bot', icon_emoji=':robot_face:')
                if '.status ' in text.lower():
                    updatedtext = re.sub('.status ', '', text, 0, 0)
                    if updatedtext in users:
                        onlinestatus = usersDict[updatedtext]
                        sc.api_call('chat.postMessage', channel=channel,
                                    text=updatedtext + " is currently " + onlinestatus + " [www.twitch.tv/" + updatedtext + "]",
                                    username='Stream Notification Bot', icon_emoji=':robot_face:')
                    else:
                        sc.api_call('chat.postMessage', channel=channel,
                                    text=updatedtext + " is not currently a part of the streamer database.",
                                    username='Stream Notification Bot', icon_emoji=':robot_face:')
                if '.help' in text.lower():
                    sc.api_call('chat.postMessage', channel=channel,
                                text="Available commands: online (see currently online streamers in database),"
                                     " streams (streamers in database), status STREAMER (check online status of"
                                     "streamer in database CASE SENSITIVE)",
                                username='Stream Notification Bot', icon_emoji=':robot_face:')
        time.sleep(delay)
        online = [] # Clear the list of online streamers so they don't exponentially stack (refreshed on each loop)
else:
    print('Failed to connect to Slack - please check token.')
