from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/compute/$', consumers.ComputeConsumer.as_asgi()),
    re_path(r'ws/run/$', consumers.RunConsumer.as_asgi()),
    re_path(r'ws/task_description/$', consumers.TaskDescriptionConsumer.as_asgi()),
    re_path(r'ws/files/$', consumers.FileListConsumer.as_asgi()),
]