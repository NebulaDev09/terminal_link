import asyncio
import json
import time
from prompt_toolkit import PromptSession, print_formatted_text


async def main():
    username = input("Please enter your username: ")
    reader, writer = await asyncio.open_connection('192.168.29.153', 6767)
    await sendSystemMessage(username, 'connected', writer)
    await asyncio.gather(send(writer, username), receive(reader))
    

async def send(writer, username):
    session = PromptSession()
    while True:
        try:
            msg =  await session.prompt_async(f"{username}: ")
            await sendMessage(username, msg, writer)

        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError) as e:
            print({e})

async def receive(reader):
    while True:
        data = await reader.readline()
        if not data:
            break
        msg = json.loads(data.decode())
        message = msg['message']
        user = msg['username']
        print_formatted_text(f"{user}: {message}")


async def sendMessage(username, message, writer):
    m = {
        'username' : username,
        'type' : 'message',
        'message' : message,
        'timestamp' : time.ctime()
    }
    data = (json.dumps(m) + '\n').encode()
    writer.write(data)
    await writer.drain()

async def sendCommand(username, command, writer):
    msg = {
        'username' : username,
        'type' : 'command',
        'command' : command,
        'timestamp' : time.ctime()
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

asyncio.run(main())