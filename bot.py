import files
import discord
import time





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
    t = time.localtime()
    current_time = time.strftime("[%H:%M]", t)
    print(f"{current_time}:login successful as {bot.user}")

    # Set status to the number that we are at


@bot.event
async def on_message(message):
    t = time.localtime()
    current_time = time.strftime("[%H:%M]", t)

    # Ignore own messages unless they are leaderboard messages, if so save them to the guild's file

    if message.author == bot.user and str(message.channel).lower() == "leaderboard":
        data = files.read(f"data/{message.guild.id}.pkl")
        data["leaderboard_message_id"] = message.id
        data["leaderboard_message_channel_id"] = message.channel.id
        files.write(f"data/{message.guild.id}.pkl", data)
        return
    else:
        try:
            if message.author == bot.user:
                data = files.read(f"data/{message.guild.id}.pkl")
                if data["leaderboard_message_channel_id"] == message.channel.id:
                    data = files.read(f"data/{message.guild.id}.pkl")
                    data["leaderboard_message_id"] = message.id
                    data["leaderboard_message_channel_id"] = message.channel.id
                    files.write(f"data/{message.guild.id}.pkl", data)
                    print(f"{current_time} on {message.guild}: non-fatal leaderboard channel was renamed")
                    return
        except KeyError:
            pass

    if message.author.bot:
        if (str(message.channel) == "leaderboard" or str(message.channel) == "counting" or message.channel == await bot.fetch_channel(data["leaderboard_message_channel_id"])) and message.author != bot.user:
            await message.delete()
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
    # dont count if messages are not send in the counting channel
    if str(message.channel) == "counting":
        # Check if message is a number
        try:
            message_number = int(message.content)
        except ValueError:
            print(f"{current_time} on {message.guild}: was looking for {expected_number} got {message.content} instead")
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


            try:
                data["till_update"] = data["till_update"] - 1
            except KeyError:
                data["till_update"] = 99

            if data["till_update"] == 0:
                data["till_update"] = 100
                try:
                    try:
                        channel = await bot.fetch_channel(data["leaderboard_message_channel_id"])
                        msg = await channel.fetch_message(data["leaderboard_message_id"])
                        await msg.delete()
                    except KeyError:
                        print(f"{current_time} on {message.guild}: No old leaderboard msg found")
                        for channel in message.guild.channels:
                            if str(channel) == "leaderboard":
                                if type(channel) == discord.channel.CategoryChannel:
                                    pass
                                else:
                                    print(f"{current_time} on {message.guild}: setup for leaderboard channel successful")
                                    data["leaderboard_message_channel_id"] = channel.id
                        try:
                            data["leaderboard_message_channel_id"]
                        except KeyError:
                            print(f"{current_time} on {message.guild}: FATAL no leaderboards channel found")
                            await message.delete()
                            return
                        pass
                    except discord.errors.NotFound:
                        print(f"{current_time} on {message.guild}: FATAL leaderboard msg not found!")
                        pass
                    # List all Counters
                    counters_value = {}
                    counters = []
                    for user in data:
                        if type(user) == int:
                            counters.append([data[user], user])
                    else:
                        # Sort output
                        counters.sort()
                        counters.reverse()
                        board = "---------Leaderboard-----------------------------\n"
                        for place in range(10):
                            try:
                                name = await bot.fetch_user(counters[place][1])
                                board += f"{place + 1}:{name}:{counters[place][0]}\n"
                            except IndexError:
                                pass
                        try:
                            channel = await bot.fetch_channel(data["leaderboard_message_channel_id"])
                        except discord.errors.NotFound:
                            print(f"{current_time} on {message.guild}: FATAL leaderboard channel deleted")
                            data = files.read(f"data/{message.guild.id}.pkl")
                            try:
                                del data["leaderboard_message_channel_id"]
                            except KeyError:
                                pass
                            files.write(f"data/{message.guild.id}.pkl", data)
                            await message.delete()
                            return
                        await channel.send(board)
                        print(f"{current_time} on {message.guild}: updated leaderboard")
                except AttributeError:
                    pass


            # updating the files

            # this prevents overwriting the leader_message_id key as the updating is handled async and is faster
            # yes i know this is not good, I will look to improve this
            try:
                data_with_id = files.read(f'data/{message.guild.id}.pkl')
                data["leaderboard_message_id"] = data_with_id["leaderboard_message_id"]
            except KeyError:
                pass
            if (data["count"] - 1) % 100 == 0:
                print(f"{current_time} on {message.guild}: Server reached {message.content}")
            files.write(f"data/{message.guild.id}.pkl", data)
        else:

            await message.delete()

    if str(message.channel) == "leaderboard":
        await message.delete()
    return


# Run the bot
try:
    bot.run(token)
except discord.errors.LoginFailure:
    print("STARTUP_ERROR: TOKEN INVALID \n deleting token.pkl")
    files.delete("data/token.pkl")
    exit(1)
