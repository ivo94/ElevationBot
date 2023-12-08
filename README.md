# ElevationBot
#### Video Demo:  <URL HERE>
#### Link to the bot: https://t.me/MrElevationBot
#### Description:
This project is a Telegram bot, implemented using the [python-telegram-bot library.](https://docs.python-telegram-bot.org/en/v20.5/index.html/)
The purpose of the bot is to tell the user the elevation at a specified location, either the location they're currently at or any location.

Telegram bots respond to commands given by the user. Each command must start with a _/_. ElevationBot has four differents commands that it can respond to:
* __/start__ : _Start the bot_
* __/help__ : _Display available commands_ 
* __/currentelevation__ : _Get the elevation at your current location_ (ask user to share it)
* __/getelevation__ : _Get the elevation at a specific place using latitude and longitude or an address_

We control what the bot will respond to user input by using what is called a _CommandHandler_. Command handlers detect the input given by the user and call a function to handle that input (a _callback_ function), for example: 
```
start_handler = CommandHandler("start", start)
```
this defines a handler for the _/start_ command, that will call the function _start_ when the command is executed by the user.
```
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I can tell you the elevation at your current location or at a specified location."
        " Use /help to see a list of available commands",
    )
```
There are quite some things that need to be explained about this function. Notice that it is defined using the keyword _async_. This means that the function will be asynchronous, which in turn means that you can use the _await_ keyword inside it. The _await_ keyword, simply explained, means that the function will pause its execution and allow the program to continue running, while the function waits for a specific event. In the _python-telegram-bot_ library, functions triggered by command handlers must be defined as asynchronous.

After having defined the command handler, we must register it so that the bot will be able to respond appropriately:
```
application.add_handler(start_handler)
```

There are other types of handlers as well. We can define message handlers with filters, that allow the bot to react to specific types of input given by the user. For instance, when the user executes the _/currentelevation_ command, the bot needs to be able to handle a _LOCATION_ type of message. This is done by using a message handler with a filter for location-type of messages:
```
application.add_handler(MessageHandler(filters.LOCATION, handle_location))
```
In this case, we are defining the handler and registering it all in one line.

Now, talking about the functioning of the bot itself, we should definetly answer the next question, how does the bot calculate the elevation at a particular location? This is done differently, depending on which way the user chooses to indicate the location:
1. The user inputs a latitude and a longitude.
2. The user inputs an address (text).

In the first case, the bot uses only the [open-elevation API](https://github.com/Jorl17/open-elevation) to get the elevation based on the latitude and longitude given. The function _fetch_elevation_ is responsible for obtaining an elevation out of the latitude longitude pair.

In the second case, when an address is given, the bot first uses the [OpenCage Geocoding API](https://opencagedata.com/api#quickstart) to transform the text into a latitude longitude pair, and then it proceeds as before.

In order to use both APIs it is necessary to get a TOKEN for both services. This is also needed in order to run the bot itself; a TOKEN is provided by Telegram, which gives the developer control over the bot. So, beware that, if you try to run the bot using only the code provided, it won't work.

So far everything we mentioned is in the main file of the project, _ElevationBot.py_. But there's another file in the folder: _test_ElevationBot.py_. As the name indicates, this file includes some tests for the functions defined before. There are tests for the functions that interact with the APIs, like test_fetch_elevation, and there also some tests for the bot behaviour, like test_start, or test_ask_location. It is relevant to say that in order the test the bot behaviour, we used python's [mock library.](https://docs.python.org/3/library/unittest.mock.html)

Even though using pytest for testing is always useuful, in this case the most direct way of testing the bot is by far using the bot itself! This was done repeatedly to ensure its correct functioning.

After testing, the bot was deployed using [Heroku](https://heroku.com/), so you can try it out yourselves at [ElevationBot.](https://t.me/MrElevationBot)
