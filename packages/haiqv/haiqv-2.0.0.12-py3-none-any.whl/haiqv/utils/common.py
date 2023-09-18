import time


def get_millis():
    return int(time.time() * 1000)


def key_subset_split(key):
    split = key.split('/')
    return split if len(split) > 1 else (key, None)
