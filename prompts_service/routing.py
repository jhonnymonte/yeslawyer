from django.urls import re_path

from prompts.consumers import PromptConsumer

websocket_urlpatterns = [
    re_path(r"ws/prompts/$", PromptConsumer.as_asgi()),
]
