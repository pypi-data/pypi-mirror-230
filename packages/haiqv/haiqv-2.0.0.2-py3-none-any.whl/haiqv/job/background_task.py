from threading import Thread, Event
from ..binding.std_bind import StdBind

import os
import signal
import psutil


class BackGroundTask:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = super().__new__(cls)
            
        return cls.__instance
    
    @classmethod
    def set_std_log_config(cls, logfile, sleep_time, fn):
        if cls.__instance is None:
            return
        cls.__instance.event = Event()
        cls.__instance.logfile = logfile
        cls.__instance.std = StdBind(logfile, cls.__instance.event, sleep_time, fn)
        cls.__instance.master_pid = os.getpid()
        cls.__instance.master_proc = psutil.Process(cls.__instance.master_pid)
        cls.__instance.th1 = Thread(target=cls.__instance.std.batch_upload_log, daemon=True)

        signal.signal(signal.SIGTERM, cls.__instance.std.signal_handler)
        signal.signal(signal.SIGINT, cls.__instance.std.signal_handler)

    @classmethod
    def start_std_log(cls):
        if cls.__instance is None:
            return
        cls.__instance.std.start()
        cls.__instance.th1.start()

    @classmethod
    def end_std_log(cls):
        # self.master_proc.send_signal(signal.SIGTERM)
        if cls.__instance is None:
            return
        cls.__instance.std.stop()
        cls.__instance.th1.join()
