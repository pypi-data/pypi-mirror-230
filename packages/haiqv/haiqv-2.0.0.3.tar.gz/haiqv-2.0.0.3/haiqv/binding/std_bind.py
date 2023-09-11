import os
import re
import sys
import signal
import traceback

from time import sleep
from threading import Thread


class StdBind():
    def __init__(self, log_name, event, sleep_time, log_artifact):
        self._stdout = None
        self._stderr = None
        self._r = None
        self._w = None
        self._thread = None
        self._on_readline_cb = None
        self.log_name = log_name
        self.event = event
        self.sleep_time = sleep_time
        self.log_artifact = log_artifact
        self.started = False

    def is_started(self):
        return self.started

    def _handler(self):
        while not self._w.closed:
            try:
                while not self._w.closed:
                    line = self._r.readline()
                    if len(line) == 0: break
                    if re.sub('(\n|\r)$', '', line):
                        with open(self.log_name, 'a', encoding='utf8') as f:
                            f.write(line)
                    self.print(line)
            except:
                break

    def signal_handler(self, signum, frame):
        if signum == signal.SIGINT or signum == signal.SIGTERM:
            self.stop()

    def batch_upload_log(self):
        while True:
            if self.event.is_set():
                break
            if os.path.isfile(self.log_name):
                self.log_artifact(self.log_name)
            sleep(self.sleep_time)

    def print(self, s, end=""):
        print(s, file=self._stdout, end=end)

    def start(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        r, w = os.pipe()
        r, w = os.fdopen(r, 'r'), os.fdopen(w, 'w', 1)
        self._r = r
        self._w = w
        sys.stdout = self._w
        sys.stderr = self._w
        self._thread = Thread(target=self._handler)
        self._thread.start()
        self.started = True

    def stop(self):
        if not self.started:
            return
        self._w.close()
        self.event.set()
        if self._thread:
            self._thread.join()
        self._r.close()
        sys.stdout = self._stdout
        sys.stderr = self._stderr
        if os.path.isfile(self.log_name):
            self.log_artifact(self.log_name)
            os.remove(self.log_name)
        self.started = False
