import logging
import requests
from opencage.geocoder import OpenCageGeocode
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from variables import TOKEN, OPEN_ELEVATION_API_KEY, GEOCODER_API_KEY, AWAIT_LOCATION
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

""" TOKEN = "6625578717:AAF3uzDQSOXpz_KGNngrb1iSROEdOeVUshM"
OPEN_ELEVATION_API_KEY = "https://api.open-elevation.com/api/v1/lookup"
GEOCODER_API_KEY = "11eff65b16674d259a4e6f4fb3443158"
AWAIT_LOCATION = 0 """
prompt_location_message = """ Tell me the location. You can use an address or a latitude and longitude. 
Example: 1600 Amphitheatre Parkway, Mountain View, CA
Example: 27.99 86.92 """

# Info about the bot execution
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# This function handles the /start command.
# The async keyword means that it is an asynchronic function.
# This means that the function can use the await keyword to pause its execution
# while waiting for a potentially slow operation to complete
# The await keyword means "wait for it"
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="I can tell you the elevation at your current location or at a specified location."
        " Use /help to see a list of available commands",
    )


# Handles the /currentElevation command
# Creates a button that allows the user to send its location
async def ask_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    location_button = KeyboardButton(text="Share Location", request_location=True)
    reply_markup = ReplyKeyboardMarkup(
        [[location_button]], resize_keyboard=True, one_time_keyboard=True
    )
    await update.message.reply_text(
        "Please share your location.", reply_markup=reply_markup
    )


# Initialize geocoder and returns a latitude and longitude based on an address passed as a parameter
def start_geocoder(address):
    # Initialize the geocoder
    geocoder = OpenCageGeocode(GEOCODER_API_KEY)
    # Geocode the address to obtain latitude and longitude
    results = geocoder.geocode(address)
    if results and len(results):
        # Extract latitude and longitude
        latitude = results[0]["geometry"]["lat"]
        longitude = results[0]["geometry"]["lng"]

        return (latitude, longitude)
    else:
        # This is returned when it was not possible to get the latitude and longitude
        return 0


# Ask the user for a location after they typed "/getelevation"
async def prompt_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(prompt_location_message)
    return AWAIT_LOCATION


""" Retrieve the elevation from the location passed by the user
The location can be given as an address or as two values representing the latitude and longitude """


async def getelevation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.strip()
    parts = user_input.split()

    # If the first character is a digit, the user tried to pass a latitude and longitude
    if user_input[0].isdigit() and len(parts) == 2:
        try:
            latitude, longitude = parts[0], parts[1]
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            await update.message.reply_text("Invalid latitude or longitude format.")
            return ConversationHandler.END

        elevation = fetch_elevation(latitude, longitude)
        await update.message.reply_text(
            f"The elevation at the specified location is {elevation} meters."
        )
        return ConversationHandler.END

    elif (len(parts) < 2):
        await update.message.reply_text(
                "Could not get the elevation for the specified address."
            )
        return ConversationHandler.END
    else:
        # If the first character is not a digit, or there are more than two parts, the user tried to pass an address
        address = user_input
        location = start_geocoder(address)
        if location != 0:
            latitude = location[0]
            longitude = location[1]
            elevation = fetch_elevation(latitude, longitude)
            await update.message.reply_text(
                f"The elevation at the specified location is {elevation} meters."
            )
            return ConversationHandler.END
        else:
            await update.message.reply_text(
                "Could not get the elevation for the specified address."
            )
            return ConversationHandler.END


def fetch_elevation(latitude, longitude):
    params = {"locations": f"{latitude},{longitude}"}
    response = requests.get(OPEN_ELEVATION_API_KEY, params=params)
    data = response.json()

    if "results" in data and data["results"]:
        elevation = data["results"][0]["elevation"]
        return elevation
    else:
        return None


""" Call the get_elevation function with the latitude and longitude obtained from the user.
Return the elevation in meters. 
Gets triggered whenever a user inputs a location. """


async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude

    elevation = fetch_elevation(latitude, longitude)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Your current elevation is {elevation} meters.",
    )


# Define the help command handler
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands_list = [
        "/start - Start the bot",
        "/help - Display available commands",
        "/currentelevation - Get the elevation at your current location",
        "/getelevation - Get the elevation at a specific place using latitude and longitude or an address",
        # Add more commands here
    ]
    commands_text = "\n".join(commands_list)
    await update.message.reply_text("Available commands:\n" + commands_text)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Unrecognized command. Try again.")


async def unknown_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Commands should start with a /")


def main():
    # Create an application object
    application = ApplicationBuilder().token(TOKEN).build()
    # Define command handlers
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    currentelevation_handler = CommandHandler("currentelevation", ask_location)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("getelevation", prompt_location)],
        states={
            AWAIT_LOCATION: [MessageHandler(filters.TEXT, getelevation)],
        },
        fallbacks=[],
    )

    # Register handlers
    application.add_handler(start_handler)
    application.add_handler(currentelevation_handler)
    application.add_handler(help_handler)
    """ MessageHandler will filter messages and trigger the handle_location function
    whenever the message contains a location """
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    application.add_handler(MessageHandler(filters.ALL, unknown_input))
    
    # Run the bot until the program stops
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()