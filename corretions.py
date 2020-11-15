import files
import discord
import os
import time

bot = discord.Client()

try:
    token = files.read("data/token.pkl")
except FileNotFoundError:
    token = input("INPUT TOKEN:")
    files.write("data/token.pkl", token)

def list_servers():
    servers = list(os.listdir("data/"))
    for server in range(len(servers)):
        edit = servers[server]
        edit = edit.replace(".pkl", "")
        servers[server] = edit
    servers.pop(len(servers)-1)
    return servers

@bot.event
async def on_ready():
    t = time.localtime()
    current_time = time.strftime("[%H:%M]", t)
    print(f"{current_time}:login successful as {bot.user}")
    servers = list_servers()

    while True:
        place = 1
        for i in servers:
            print(f"{place}:{await bot.fetch_guild(i)}")
            place += 1
        server_select = input(">>>")
        try:
            data = files.read(f"data/{servers[int(server_select)-1]}.pkl")
        except (IndexError, ValueError):
            print("You have to select a valid server")
            continue
        while True:
            while True:
                action_counter = 1
                for i in data:
                    if type(i) == str:
                        print(f"{action_counter}:{i} = {data[i]}")
                    else:
                        print(f"{action_counter}:{await bot.fetch_user(i)} = {data[i]}")
                    action_counter += 1
                action_select = input(">>>")
                try:
                    int(action_select)
                    break
                except ValueError:
                    print("Not Valid number")
            action_counter = 1
            for i in data:
                if action_counter == int(action_select):
                    action = i
                    break
                else:
                    pass
                action_counter += 1
            try:
                confirmation = input(f"Do you want to edit {await bot.fetch_user(action)}? \n>>>")
            except discord.errors.HTTPException:
                confirmation = input(f"Do you want to edit {action}? \n>>>")
            if confirmation.lower() == "y":
                pass
            else:
                continue
            new_value = input("Set new value \n>>>")
            try:
                data[action] = int(new_value)
            except ValueError:
                data[action] = new_value
            files.write(f"data/{servers[int(server_select)-1]}.pkl", data)


bot.run(token)
