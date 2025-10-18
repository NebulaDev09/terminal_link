import asyncio
import json

clients = set()

async def handle_clients(reader, writer):
    clients.add(writer)
    while True:
        data = await reader.readline()
        if not data:
            break
        message = json.loads(data.decode())
        if message == "":
            break
        if message['type'] == 'message':
            for client in list(clients):
                if client != writer:
                    try:
                        client.write((json.dumps(message) + '\n').encode())
                        await writer.drain()
                    except (ConnectionError, ConnectionRefusedError, ConnectionResetError):
                        clients.remove(client)


async def main():
    server = await asyncio.start_server(handle_clients, '192.168.29.153', 6767)
    async with server:
        await server.serve_forever()
asyncio.run(main())
