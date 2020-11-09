import discord
import files

bot = discord.Client()
try:
    token = files.read("data/token.pkl")
except FileNotFoundError:
    token = input("INPUT TOKEN:")
    files.write("data/token.pkl", token)

# TODO
# Delete leaderboard messages


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

    # Set status to the number that we are at


@bot.event
async def on_message(message):
    # Ignore own messages unless they are leaderboard messages, if so save them to the guild file
    if message.author == bot.user and (message.content.startswith("---------Leaderboard-----") or message.content.startswith('Type "Update" to get a new leaderboard') or message.content.startswith("There are no Counters on")):
        data = files.read(f"data/{message.guild.id}.pkl")
        data["leaderboard_message_id"] = message.id
        data["leaderboard_message_channel_id"] = message.channel.id
        files.write(f"data/{message.guild.id}.pkl", data)
    if message.author.bot:
        return

    # Put server's data into var data for efficiency
    try:
        data = files.read(f"data/{message.guild.id}.pkl")
    except FileNotFoundError:
        files.write(f"data/{message.guild.id}.pkl", {"count": 1})
        data = files.read(f"data/{message.guild.id}.pkl")
    except AttributeError:
        await message.channel.send("Sorry you have to be on a server to count")
        return

    expected_number = data["count"]
    print(f"expected number = {expected_number}")
    # dont count if messages are not send in the counting channel
    if str(message.channel) == "counting":
        # Check if message is a number
        try:
            message_number = int(message.content)
        except ValueError:
            # If not delete the message
            await message.delete()
            return

        # ignore if the author of the message was the last one counting
        try:
            if message.author.id == data["last_counter"]:
                await message.channel.send(f"Sie sind der letzte der Zählte, **{message.author}**!")
                await message.delete()
                return
        except KeyError:
            pass

        # delete message if the number isn't the one we're searching for
        if message_number == expected_number:
            # Update Values

            data["count"] = data["count"] + 1
            data["last_counter"] = message.author.id
            try:
                # Read participation data add 1 to user's value
                participation_user = data[message.author.id]
                participation_user = participation_user + 1
                data[message.author.id] = participation_user

            except KeyError:
                # If participation is not there yet set it to one
                data[message.author.id] = 1

            # updating the files
            files.write(f"data/{message.guild.id}.pkl", data)

        else:

            await message.delete()

    if str(message.channel) == "leaderboard":
        try:
            # Retrieve the message and channel id and delete the old message
            try:
                channel = await bot.fetch_channel(data["leaderboard_message_channel_id"])
                msg = await channel.fetch_message(data["leaderboard_message_id"])
                await msg.delete()
            except discord.NotFound:
                pass
        except KeyError:
            pass
        if message.content.lower() == "update":

            # List all Counters
            counters_value = {}
            counters = []
            for user in data:
                if type(user) == int:
                    counters.append([data[user], str(await bot.fetch_user(user))])
            if not counters:
                await message.channel.send(f"There are no Counters on {message.guild} :(")
            else:
                # Sort output
                counters.sort()
                counters.reverse()
                board = "---------Leaderboard-----------------------------\n"
                for place in range(len(counters)):
                    board += f"{place + 1}:{counters[place][1]}:{counters[place][0]}\n"

                await message.channel.send(board)

        else:
            await message.channel.send('Type "Update" to get a new leaderboard ')
        await message.delete()
    return


# Run the bot
try:
    bot.run(token)
except discord.errors.LoginFailure:
    print("TOKEN INVALID")
    files.delete("data/token.pkl")
    exit(1)
