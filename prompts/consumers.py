import json

from channels.generic.websocket import AsyncWebsocketConsumer


class PromptConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = getattr(self.scope, "user", None)
        await self.accept()
        if self.user and getattr(self.user, "is_authenticated", False):
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.send(
                text_data=json.dumps({"message": "WebSocket conectado", "user_id": self.user.id})
            )
        else:
            self.group_name = None
            await self.send(text_data=json.dumps({"message": "WebSocket conectado (anónimo)"}))

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            prompt = data.get("prompt", "")
        except json.JSONDecodeError:
            prompt = text_data.strip()

        await self.send(text_data=json.dumps({"response": f"Echo: {prompt}"}))

    async def disconnect(self, close_code):
        if getattr(self, "group_name", None):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        return

    async def prompt_message(self, event):
        await self.send(text_data=json.dumps(event))
