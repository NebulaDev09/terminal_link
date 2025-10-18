import asyncio
import json
import time
from prompt_toolkit import PromptSession


async def main():
    session = PromptSession()
    username = input("Please enter your username: ")
    reader, writer = await asyncio.open_connection('192.168.29.153', 6767)
    await sendSystemMessage(username, 'connected', writer)
    while True:
        try:
            msg =  await session.prompt_async(f"{username}: ")
            await sendMessage(username, msg, writer)

        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError) as e:
            print({e})

        except KeyboardInterrupt:
            await sendSystemMessage(username, 'disconnected', writer)
            writer.close()
            await writer.wait_closed()
            break
    

async def sendMessage(username, message, writer):
    m = {
        'username' : username,
        'type' : 'message',
        'command' : message,
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