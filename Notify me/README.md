# NotifyMe
Command-line program to send a telegram message via a bot.

## Usage
``` bash
notify_me.py [-h] -m M [-f F]
```

Opens a file called secrets.txt containing and reads constants:
- API
- CHAT_ID

API is the bot's API key.
CHAT_ID is the id of the specific chat you wish to send a message to.

## Creating a bot
In Telegram, create a chat with @BotFather.

Send it a message "/newbot" and follow instructions.

Be sure to copy your bot's API key.

## Getting the chat id
Search for the bot and send it any message.

Open a web browser and paste the following link (be sure to substitute <botAPI>):

``` url
https://api.telegram.org/bot<botAPI>/getUpdates
```

The response will contain chat>id.