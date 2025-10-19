#this code runs on my hopes and dreams

import asyncio #for the networking
import json # better format to send data in?
import time # to display timestamps
from prompt_toolkit import PromptSession, print_formatted_text # promp session for async input and print_formatted_text so the new text doesnt overwrite the user input
from prompt_toolkit.formatted_text import FormattedText # add colors
from InquirerPy import inquirer # selecting room thing in the terminal, similar to how you can select when you do npm create project
from concurrent.futures import ThreadPoolExecutor # to convert the selecting thing into a async input, since that wasnt included in the library

executor = ThreadPoolExecutor()


async def async_select(message, choices):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        executor,
        lambda: inquirer.select(message=message, choices=choices).execute()
    ) #Convert selecting thing in the terminal to async so it doesnt break the program, since normal input just blocks all other async functions that are happening


color = '#ffffff'
in_room = False


async def input_async(prompt_text: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: input(prompt_text))


async def main():
    global session 
    session = PromptSession()
    username = await session.prompt_async("Please enter your username: ")
    reader, writer = await asyncio.open_connection('192.168.29.153', 6767)
    await sendServerMessages(username, 'connected', writer)
    data = await reader.readline() #recieve room list
    rooms = json.loads(data.decode())
    await chooseRoom(rooms, username, writer, reader)


async def chooseRoom(rooms, username, writer, reader):
    choices = []
    for room in rooms:
        choices.append(f"{room} ({rooms[room]})")
    create_label = "(+) Create a new room"
    choices.append(create_label)
    selection = await async_select(message="Join or create a room:", choices=choices)
    if selection == create_label:
        new_room = await session.prompt_async("Enter new room name: ")
        room = new_room.strip()
    await joinRoom(username, room, writer, reader)


async def joinRoom(username, room, writer, reader):
    msg = {
        'username' : username,
        'type' : 'system',
        'event' : "roomJoin",
        'room' : room,
        'timestamp' : time.ctime(),
        'color' : '#ffffff'
    }
    data = (json.dumps(msg) + '\n').encode()
    writer.write(data)
    await writer.drain()
    # send and receive at the same time
    await asyncio.gather(send(writer, username), receive(reader))


async def send(writer, username):
    session = PromptSession()
    global color
    while True:
        try:
            msg = await session.prompt_async(FormattedText([(color, f"{username}: ")]))
            if not msg:
                continue
            if msg[0] == '/':
                c = msg.split()
                command = c[0][1:]
                if command == 'color' or command == 'colour':
                    if len(c) >= 2:
                        new_color = c[1]
                        color = new_color
                        await sendCommand(username, msg, writer)
                elif command == 'nick':
                    if len(c) >= 2:
                        username = c[1]
                        await sendCommand(username, msg, writer)
                elif command == 'exit':
                    await sendSystemMessage(username, 'disconnected', writer)
                    await chooseRoom()
            else:
                await sendMessage(username, msg, writer)

        except ConnectionRefusedError:
            print_formatted_text("Cannot connect to the server")
            break
        except ConnectionAbortedError:
            print_formatted_text("Connection compromised, please switch to a secure server")
            break
        except (EOFError, KeyboardInterrupt): #ctlr + c
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
            break


async def receive(reader):
    while True:
        data = await reader.readline()
        if not data:
            break
        try:
            msg = json.loads(data.decode())
        except Exception:
            continue
        mtype = msg.get('type')
        if mtype == 'message':
            message = msg['message']
            user = msg["username"]
            col = msg["color"]
            print_formatted_text(FormattedText([(col, f"{user}: {message}")]))
        elif mtype == 'system':
            event = msg["event"]
            user = msg["username"]
            print_formatted_text(f"[system] {user} {event}")


async def sendMessage(username, message, writer):
    m = {
        'username' : username,
        'type' : 'message',
        'message' : message,
        'timestamp' : time.ctime(),
        'color' : color
    }
    data = (json.dumps(m) + '\n').encode()
    writer.write(data)
    await writer.drain()


async def sendCommand(username, command, writer):
    msg = {
        'username' : username,
        'type' : 'command',
        'command' : command,
        'timestamp' : time.ctime(),
        'color' : '#ffffff'
    }
    data = (json.dumps(msg) + '\n').encode()
    writer.write(data)
    await writer.drain()


async def sendSystemMessage(username, event, writer):
    msg = {
        'username' : username,
        'type' : 'system',
        'event' : event,
        'timestamp' : time.ctime()
    }
    data = (json.dumps(msg) + '\n').encode()
    writer.write(data)
    await writer.drain()


async def sendServerMessages(username, event, writer):
    msg = {
        'username' : username,
        'type' : 'server',
        'event' : event,
        'timestamp' : time.ctime()
    }
    data = (json.dumps(msg) + '\n').encode()
    writer.write(data)
    await writer.drain()


async def dbCommands(username, command, writer):
    return

asyncio.run(main())