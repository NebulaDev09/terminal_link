import asyncio
import json

async def handle_echo(reader, writer):
    while True:
        data = await reader.readline()
        if not data:
            break
        message = data.decode().strip()
        if message == "":
            break
        print(message)

async def main():
    server = await asyncio.start_server(handle_echo, '192.168.29.153', 6767)
    async with server:
        await server.serve_forever()
asyncio.run(main())
