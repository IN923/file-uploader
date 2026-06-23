# consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ProgressConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        print("hhhfdfdfdffdfddddddddddd")
        self.job_id = self.scope["url_route"]["kwargs"]["job_id"]
        print("self.scope url route",self.scope["url_route"]["kwargs"]["job_id"])
        self.group_name = f"job_{self.job_id}"
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
        # print("progress data=",event["data"].keys())
        # print("progress values=",event["data"].values())
#   // const [files,setFiles] = useState([]);
#   // const files = [{
#   //   'id': 1,
#   //   'progress': 45,
#   //   'status': 'completed',
#   //   'file': 'AB'
#   // }]

        await self.send(
            text_data=json.dumps(event["data"])
        )

class TestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("✅ WebSocket connected")
        await self.accept()

    async def disconnect(self, close_code):
        print(f"❌ WebSocket disconnected: {close_code}")