import urllib
import os
import time
import hashlib
import pickle
import colorama

USER_HOME_DIR = os.path.expanduser("~")


def cache_file():
    if not os.path.exists(os.path.join(USER_HOME_DIR, ".mcrsrctool")):
        os.makedirs(os.path.join(USER_HOME_DIR, ".mcrsrctool"))
    if not os.path.exists(os.path.join(USER_HOME_DIR, ".mcrsrctool", "cacheindex")):
        open(os.path.join(USER_HOME_DIR, ".mcrsrctool", "cacheindex"), "w").close()
    if not os.path.exists(os.path.join(USER_HOME_DIR, ".mcrsrctool", "cache")):
        os.makedirs(os.path.join(USER_HOME_DIR, ".mcrsrctool", "cache"))
    f = open(os.path.join(USER_HOME_DIR, ".mcrsrctool", "cacheindex"), "r")
    try:
        return pickle.load(f)
    except EOFError:
        return {}


def cache_file_save(cache):
    if not os.path.exists(os.path.join(USER_HOME_DIR, ".mcrsrctool")):
        os.makedirs(os.path.join(USER_HOME_DIR, ".mcrsrctool"))
    if not os.path.exists(os.path.join(USER_HOME_DIR, ".mcrsrctool", "cacheindex")):
        open(os.path.join(USER_HOME_DIR, ".mcrsrctool", "cacheindex"), "w").close()
    if not os.path.exists(os.path.join(USER_HOME_DIR, ".mcrsrctool", "cache")):
        os.makedirs(os.path.join(USER_HOME_DIR, ".mcrsrctool", "cache"))
    f = open(os.path.join(USER_HOME_DIR, ".mcrsrctool", "cacheindex"), "w")
    pickle.dump(cache, f)


def cache_get(url):
    cache = cache_file()
    print colorama.Fore.LIGHTBLUE_EX + "\tDownloading file from", colorama.Fore.WHITE + url
    if url in cache:
        if int(time.time()) < cache[url][1]:
            print colorama.Fore.LIGHTBLUE_EX + "\t\tAlready found in cache, using that"
            return cache[url][0]
    urllib.urlretrieve(url, os.path.join(USER_HOME_DIR, ".mcrsrctool", "cache", hashlib.md5(url).hexdigest()))

    expire = int(time.time()) + 3 * 24 * 60 * 60
    cache[url] = [os.path.join(USER_HOME_DIR, ".mcrsrctool", "cache", hashlib.md5(url).hexdigest()), expire]

    cache_file_save(cache)
    return os.path.join(USER_HOME_DIR, ".mcrsrctool", "cache", hashlib.md5(url).hexdigest())
