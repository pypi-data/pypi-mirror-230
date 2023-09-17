# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2021 Michał Góral.

import queue
import multiprocessing as mp
import traceback
from collections import deque
from contextlib import contextmanager
from http.server import HTTPServer, SimpleHTTPRequestHandler
import logging

from stag.utils import chdir

log = logging.getLogger(__name__)


class Process(mp.Process):
    def __init__(self, target, args=None, kwargs=None):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        self._queue = mp.Queue()
        self._unhandled = {}

        args = (self._queue,) + args
        super().__init__(target=target, args=args, kwargs=kwargs)

    def run(self):
        try:
            super().run()
        except Exception as e:
            tb = traceback.format_exc()
            self._queue.put(("exception", (e, tb)))

    @property
    def exception(self):
        return self.get_message("exception")

    def get_message(self, name: str, block=False):
        try:
            while True:
                msg_name, msg = self._queue.get(block)
                if msg_name == name:
                    return msg
                self._unhandled.setdefault(msg_name, deque()).append(msg)
        except queue.Empty:
            return self._get_first_unhandled_message(name)

    def _get_first_unhandled_message(self, name: str):
        messages = self._unhandled.get(name, deque())
        try:
            return messages.popleft()
        except IndexError:
            return None


# This function is intended to be run in a separate process
def run_http_server(q, directory, port):
    with chdir(directory):
        log.info("Serving files from %s", directory)
        server_address = ("", port)
        httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
        log.info("Running simple HTTP server on http://localhost:%d", httpd.server_port)
        q.put(("address", httpd.server_address))
        httpd.serve_forever()


@contextmanager
def run_server(serve_directory, port):
    server = Process(target=run_http_server, args=(serve_directory, port))
    try:
        server.start()
        yield server
    finally:
        log.info("Terminating HTTP server.")
        server.terminate()
        server.join()
        server.close()
