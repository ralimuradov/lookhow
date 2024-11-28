import asyncio
import websockets
import logging

IP = '127.0.0.1'
PORT = '8001'

#------------------------------------------------------------------------

connected_clients = set()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handler(websocket, path):
    logger.info('Server started')

    with open('apps/shared_file.txt', 'r+') as shared_file:
        text_content = shared_file.read()
        
    connected_clients.add(websocket)

    try:
        await websocket.send(text_content)
        async for message in websocket:
            websockets.broadcast(connected_clients, message)
            with open('apps/shared_file.txt', 'w') as shared_file:
                shared_file.write(message)
    finally:
        connected_clients.remove(websocket)

start_server = websockets.serve(handler, IP, PORT)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
