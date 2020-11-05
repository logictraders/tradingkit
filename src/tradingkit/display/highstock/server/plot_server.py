#!/usr/bin/env python


import asyncio
import json
import logging
import multiprocessing

import websockets


class PlotServer:

    def __init__(self, port):
        self.port = port
        self.DATA = {'price': {"OHLC": [],
                               "close": [],
                               "volume": [],
                               "pos_vol": [],
                               "equity": [],
                               "base_equity": [],
                               "invested": [],
                               "hold": [],
                               "pos_p": []
                               },
                     'buy': [], 'sell': [], 'assets': []}
        self.NEW_DATA = {}

        self.USERS = set()

    def state_event(self):
        return json.dumps({"type": "start", "data": self.DATA})

    def update_event(self):
        return json.dumps({"type": self.NEW_DATA['type'], "data": self.NEW_DATA['data']})

    async def notify_state(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.state_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def notify(self):
        if self.USERS:  # asyncio.wait doesn't accept an empty list
            message = self.update_event()
            await asyncio.wait([user.send(message) for user in self.USERS])

    async def register(self, websocket):
        self.USERS.add(websocket)

    async def unregister(self, websocket):
        self.USERS.remove(websocket)

    async def update(self, websocket, path):
        try:
            async for message in websocket:
                payload = json.loads(message)
                if payload["action"] == "produce":
                    if payload['type'] == "price":
                        for key in payload['data'].keys():
                            # print(key)
                            self.DATA['price'][key].append(payload['data'][key])
                        self.NEW_DATA['data'] = payload['data']
                        self.NEW_DATA['type'] = payload['type']
                    elif payload['type'] == "buy":
                        self.NEW_DATA['data'] = payload['data']
                        self.NEW_DATA['type'] = payload['type']
                        self.DATA['buy'].append(payload['data'])
                    elif payload['type'] == "sell":
                        self.NEW_DATA['data'] = payload['data']
                        self.NEW_DATA['type'] = payload['type']
                        self.DATA['sell'].append(payload['data'])
                    else:
                        self.DATA[payload['type']].append(payload['data'])

                    await self.notify()
                elif payload["action"] == "start":
                    await self.notify_state()
                elif payload["action"] == "register":
                    await self.register(websocket)
                else:
                    logging.error("unsupported event: {}", payload)
        finally:
            if websocket in self.USERS:
                await self.unregister(websocket)

    def run(self):
        start_server = websockets.serve(self.update, "localhost", self.port)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()


# ps = PlotServer()
# ps.run()
# print("running...")

if __name__ == '__main__':
    ps = PlotServer()
    p = multiprocessing.Process(target=ps.run)
    p.start()
    print("running...")
