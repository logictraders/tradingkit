import os
import re
import socketserver
from http.server import SimpleHTTPRequestHandler
from typing import Tuple, Optional, Union


class RequestHandler(SimpleHTTPRequestHandler):

    def __init__(self, routing: dict, *args, **kwargs):
        self.routing = routing if routing else None
        super().__init__(*args, **kwargs)

    def translate_path(self, path):
        if self.routing:
            for pattern in self.routing:
                if path.startswith(pattern):
                    return os.path.join(self.routing[pattern], path[len(pattern):])
        return super().translate_path(path)
