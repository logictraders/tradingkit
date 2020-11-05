import functools
import logging
import random
import socketserver
import time
from multiprocessing.context import Process

from tradingkit.utils.request_handler import RequestHandler


class WebServer:

    @staticmethod
    def serve(routing: dict, open_browser=False, timeout=None, filename=''):
        p = Process(target=WebServer.serve_and_browse, args=(routing, open_browser, filename, ))
        p.start()
        wait_for_server_seconds = timeout
        logging.info("Waiting for server %d seconds" % wait_for_server_seconds)
        time.sleep(wait_for_server_seconds)
        p.terminate()

    @staticmethod
    def serve_and_browse(routing: dict, open_browser=False, filename=''):
        handler = functools.partial(RequestHandler, routing)
        port = random.randint(1024, 65535)
        with socketserver.TCPServer(("", port), handler) as httpd:
            if open_browser:
                import webbrowser
                webbrowser.open_new_tab('http://localhost:%d%s' % (port, filename))
            print("serving at port", port)
            httpd.serve_forever()
