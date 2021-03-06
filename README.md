# twitchOnline
Check if streamers from a list of specified streamers go live on Twitch

## Dependencies
* Python 3
* Requests (for making calls to the New Twitch API)
* Regular Expressions (for parsing and cleaning received data)
* Time (Delays between subsequent calls)
* SlackClient (Slack API for notifications + commands) **OR** Discord.py (Discord module for notifications + commands)
  * Dependent on which program you decide to use

## What It Does
twitchOnline monitors a list of Twitch streamers that you input and sends a message in a designated Slack or Discord channel when one of them goes live. Also provides command functionality for more flexibility. If you're curious regarding the process in which I developed this script, you can check out my blog post [here](https://thecompanyproject.wordpress.com/2018/07/17/tol-online-broadcast-bot/).

## Necessary Input
In order to make the code work, you must modify the following in the code:
* Input Twitch Client ID (guide on how to find yours [here](https://docs.aws.amazon.com/lumberyard/latest/userguide/chatplay-generate-twitch-client-id.html))
* Streams to check (alter "users" variable with a list of strings as stream names, names should be lowercase)
* For Slack Version:
  * Slack Channel to send messages to
  * Slack Token (search it up, pretty easy to find)
* For Discord Version:
  * Discord Channel ID to send messages to (enable developer options and copy the channel ID)
  * Discord Bot Token (guide on how to find it [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token))

## Commands
* Slack Version
  * .online - gives a list of all online streams (from given list of streams to check for).
  * .streams - gives a full list of streams being monitored.
  * .help - gives a list of all available commands (hard coded in).
  * .status STREAMNAME - replace STREAMNAME with a stream name (case sensitive to given stream list) to check the current status of the stream (online/offline). Also provides a link to the stream.
* Discord Version
  * !online - gives a list of all online streams (from given list of streams to check for).
  * !uptime STREAMNAME - gives the start time of an online streamer (must also be in databse)

## Important Notes
* The New Twitch API handles capitalization of names in cURL requests weird. I've found that keeping stream usernames in the list of names to check for in all lowercase works.
* The New Twitch API has delays in being refreshed. As such, notifications are not immediate and from my experience, take up to 3 minutes for changes to be pushed to live.
* The .status command (Slack only) is case sensitive and must be matched to the capitalization input in the 'users' variable
* New Twitch API can only handle a maximum of 100 users in a cURL request. If you require more than 100 users, make a second request with the additional users.

## Nonexistent Roadmap
No guarantees I'll ever get to these since I usually abandon projects once they're done (or sometimes when they aren't done).
* Remove case sensitivity in commands and user input
* Adding full command functionality to Discord version
* Issues with Twitch requests giving false offline positives, will implement a confirmation system to reduce false positives

## Special Thanks
Thanks to the following articles as they helped in various functionality with this script:
* Using Python & Slack for Quick and free personal push notifications, Matt Harvey, Aug 7 2018
  * Used as a baseline reference for sending messages through Slack
* Automatically respond to Slack messages containing specific text, Paweł Fertyk, November 1, 2016
  * Used as a reference for creating commmands in Slack
* Discord background task example
  * Reference for running background tasks rather than awaiting user commands
* How To Index and Slice Strings in Python 3, Lisa Tagliaferri, September 28, 2016
  * Used to parse Twitch response data for streamer names to locate stream titles
