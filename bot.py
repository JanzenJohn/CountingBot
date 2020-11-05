import discord
import files


bot = discord.Client()
token = files.read("token.pkl")

# Check if every required file exists
required_files = ["last_user.pkl", "number.pkl"]
for file in required_files:
    try:
        files.read(file)
    except FileNotFoundError:
        files.write(file, 1)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

    # Set status to the number that we are at
    await bot.change_presence(activity=discord.Game(str(files.read("number.pkl")-1)))


@bot.event
async def on_message(message):
    # Ignore own messages
    if message.author == bot.user:
        return

    # Ignore messages not send in the counting channel
    if str(message.channel) != "counting":
        return

    # get the number we are currently at
    current_number = files.read("number.pkl")

    # Check if message is a number
    try:
        message_number = int(message.content)
    except ValueError:
        # If not delete it
        await message.delete()
        return

    # ignore if the author of the message was the last one counting
    if message.author.id == files.read("last_user.pkl"):
        await message.channel.send(f"Sie sind der letzte der Zählte, **{message.author}**!")
        await message.delete()
        return

    # delete message if the number isn't the one we're searching for
    if message_number == current_number:
        # Update the files to represent the new number, counter
        files.write("number.pkl", current_number+1)
        files.write("last_user.pkl", message.author.id)

        # Update the discord status
        await bot.change_presence(activity=discord.Game(str(files.read("number.pkl")-1)))

    else:

        await message.delete()


# Run the bot
bot.run(token)
