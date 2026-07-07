# consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .tasks import *

class ProgressConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_id = self.scope["url_route"]["kwargs"]["uname"]
        print("self.scope url route",self.scope["url_route"]["kwargs"]["uname"])
        # self.group_name = f"user_{self.user_id}"
        self.group_name = f"{self.user_id}"
        print("self.group_name",self.group_name)
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        print(self.channel_layer)
        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def progress_update(self, event):
        print("progress update getting executed")
        await self.send(
            text_data=json.dumps(event["data"])
        )

    async def merge_status(self,event):
        print("message sent by celery task=",event)
        # await self.send(text_data=event[  ])
        if event["msg"]=='success':
            print("celery success meeeeeeeeeeee")
            upload_file.delay(event['socketname'],file_item=event['unique_name'],filename=event['filename'])

        # await self.send(text_data=json.dumps({
        #     "msg": event["msg"],
        # })) 

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("✅ WebSocket connected")
        print(f"self.scope={self.scope}")
        print("gggggggg=",self.channel_layer.group_add("inder",self.channel_name))
        await self.accept()

    async def disconnect(self, close_code):
        print(f"❌ WebSocket disconnected: {close_code}")

# class MergingStatus(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user_id = self.scope["url_route"]["kwargs"]["uname"]
#         print("self.scope url route",self.scope["url_route"]["kwargs"]["uname"])
#         # self.group_name = f"user_{self.user_id}"
#         self.group_name = f"{self.user_id}"
#         print("self.group_name",self.group_name)
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )
#         print(self.channel_layer)
#         await self.accept()

#     async def disconnect(self,close_code):
#         print(f"❌ WebSocket disconnected: {close_code}")

#     async def merge_status(self,event):
#         print("message sent by celery task=",event)
#         # await self.send(text_data=event[  ])
#         if event["msg"]=='success':
#             upload_file.delay(event['socketname'],filename=event['filename'])

#         # await self.send(text_data=json.dumps({
#         #     "msg": event["msg"],
#         # }))
