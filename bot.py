import files
import discord
import time
import os


bot = discord.Client()

# load the Token into a variable / ask for it
try:
    token = files.read("data/token.pkl")
except FileNotFoundError:
    token = input("INPUT TOKEN:")

    # the writing of the token.pkl file does not automatically generate a data folder
    # this creates it if it is missing

    try:
        files.write("data/token.pkl", token)
    except FileNotFoundError:
        os.system("mkdir data")
        files.write("data/token.pkl", token)




# TODO
# nothing rn


@bot.event
async def on_ready():
    t = time.localtime()
    current_time = time.strftime("[%H:%M]", t)
    print(f"{current_time}:login successful as {bot.user}")
    # downloads the 


@bot.event
async def on_message(message):
    t = time.localtime()
    current_time = time.strftime("[%H:%M]", t)

    # Ignore own messages unless they are leaderboard messages, if so save them to the guild's file

    if message.author == bot.user:
        data = files.read(f"data/{message.guild.id}.pkl")

        # Write the channel id and message id (dependent on channel) into the guild file
        try:
            if message.channel.id == data["leaderboard_message_channel_id"]:
                data["leaderboard_message_id"] = message.id
                files.write(f"data/{message.guild.id}.pkl", data)
                return
        except KeyError:
            if str(message.channel).lower() == "leaderboard":
                data["leaderboard_message_id"] = message.id
                data["leaderboard_message_channel_id"] = message.channel.id
                files.write(f"data/{message.guild.id}.pkl", data)

    if message.author.bot:
        forbidden = ["leaderboard", "counting"]
        data = files.read(f"data/{message.guild.id}.pkl")
        if (str(message.channel) in forbidden or message.channel.id == data["leaderboard_message_channel_id"]) and message.author != bot.user:
            await message.delete()
        return



    # Put server's data into var data for efficiency

    try:
        data = files.read(f"data/{message.guild.id}.pkl")
    except FileNotFoundError:

        # if the file is not found intitialize the guild with counter on 1
        files.write(f"data/{message.guild.id}.pkl", {"count": 1})
        data = files.read(f"data/{message.guild.id}.pkl")
    except AttributeError:

        # This only occurs in a private chat
        await message.channel.send("Sorry you have to be on a server to count")
        return
    try:
        expected_number = int(data["count"])
    except ValueError:
        # This prevents breaking of functionality when the Value is a string as a result of corrections.py
        expected_number = 1
    # dont count if messages are not send in the counting channel

    if str(message.channel) == "counting":
        # Check if message is a number
        # If not disregard the message and delete it
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
            # Update Values for counting

            data["count"] = expected_number + 1
            data["last_counter"] = message.author.id
            try:
                # Read participation data add 1 to user's value
                participation_user = data[message.author.id]
                participation_user = participation_user + 1
                data[message.author.id] = participation_user

            except KeyError:
                # If participation is not there yet set it to one
                data[message.author.id] = 1

            # this is used for updating the leaderboard
            try:
                data["till_update"] = data["till_update"] - 1
            except KeyError:
                data["till_update"] = 99

            # <= because of caution IF something goes wrong that decreases the till_update key to a negative
            # or stupid / not intended use of corrections.py
            if data["till_update"] <= 0:
                data["till_update"] = 100

                # Jup i have 0 clues on why attribute errors are excepted here
                # will test later it's 1am so no not now
                try:

                    # Ignore if leaderboard messages haven't been configured yet, is normal on first run
                    try:
                        channel = await bot.fetch_channel(data["leaderboard_message_channel_id"])
                        msg = await channel.fetch_message(data["leaderboard_message_id"])
                        await msg.delete()
                        # delete old Message so you dont have multiple leaderboards, done first bc even when something
                        # goes wrong, there shall be now indication of that on the discord users end only logs
                    except KeyError:
                        print(f"{current_time} on {message.guild}: No old leaderboard msg found")
                        for channel in message.guild.channels:
                            # this could potentionally reconfigure the leaderboard channel without will,
                            # however in order for this to happen, the KeyError has to be raised by the "leaderboard_message_id" key
                            # this key is always defined except on first run
                            # aka when no leaderboard channel is defined anyways
                            # the only exception being someone working with corrections.py
                            # TODO
                            # make this specific to "leaderboard_message_channel_id" key
                            if str(channel) == "leaderboard":
                                if type(channel) == discord.channel.CategoryChannel:
                                    pass
                                else:
                                    print(f"{current_time} on {message.guild}: setup for leaderboard channel successful")
                                    data["leaderboard_message_channel_id"] = channel.id
                        try:
                            # This is only undefined when the setup above fails to locate any channels named "leaderboard"
                            data["leaderboard_message_channel_id"]
                        except KeyError:
                            print(f"{current_time} on {message.guild}: FATAL no leaderboards channel found")
                            # user counts are deleted to ensure that no Errors will hinder the count from being valid
                            # will look into this, maybe making a leaderboardless version idk
                            await message.delete()
                            return
                        pass
                    except discord.errors.NotFound:
                        print(f"{current_time} on {message.guild}: FATAL leaderboard msg not found!")
                        pass
                    # List all Counters
                    counters = []
                    for user in data:
                        if type(user) == int:
                            counters.append([data[user], user])
                    else:
                        # Sort output
                        counters.sort()
                        # we dont wan't the lowest on the leaderboard
                        counters.reverse()
                        board = "---------Leaderboard-----------------------------\n"
                        for place in range(10):
                            try:
                                name = await bot.fetch_user(counters[place][1])
                                board += f"{place + 1}:{name}:{counters[place][0]}\n"
                            except IndexError:
                                pass

                        # I should probably move this check to the others
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


            # updating the guild file

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
        # As all bot actions quit the function before so this is safe
        await message.delete()
    return


# Run the bot
try:
    bot.run(token)
except discord.errors.LoginFailure:
    print("STARTUP_ERROR: TOKEN INVALID \n deleting token.pkl")
    files.delete("data/token.pkl")
    exit(1)
