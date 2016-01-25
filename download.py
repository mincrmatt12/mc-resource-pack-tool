import json
import os
import shutil
import urllib
from colorama import Fore, Back, Style
import cache
import zipfile
import shutil

prgrs = 0


def create_urllib_reporthook(nm):
    global prgrs
    prgrs = 0

    def urllib_reporthook(blocks, size, amt):
        global prgrs
        total = (blocks * size) / 1024.0
        print "\r" + Fore.LIGHTBLUE_EX + "\tDownloading file", Fore.WHITE + nm, Fore.LIGHTBLUE_EX + "({0:.2f}KB of {1:.2f}KB)".format(total, amt/1024.0),

    return urllib_reporthook


class MCVersion:
    def __init__(self, version):
        self.ver = version["id"]
        self.type = version["type"]

    def asset_ver(self):
        other_data = grab_json("http://s3.amazonaws.com/Minecraft.Download/versions/{0}/{0}.json".format(self.ver))
        ass = other_data["assets"]
        rt = ""
        for i in ass:
            if i == ".": continue
            rt += i
        return int(rt)


    def get_assets(self, dir_, cache_):
        dir_ = os.path.join(dir_, "assets")
        cache_ = os.path.join(cache_, "assets")
        print Fore.GREEN + "Downloading assets for", Fore.WHITE + self.ver
        other_data = grab_json("http://s3.amazonaws.com/Minecraft.Download/versions/{0}/{0}.json".format(self.ver))
        asset_link = "https://s3.amazonaws.com/Minecraft.Download/indexes/{}.json".format(other_data["assets"])
        asset_hashes = grab_json(asset_link)
        objects = asset_hashes["objects"]
        for object in objects:
            name = object
            data = objects[object]
            hash = data["hash"]
            hp = hash[:2]
            pth = os.path.join(dir_, os.path.dirname(name))
            if not os.path.exists(pth):
                os.makedirs(pth)
            pth = os.path.join(dir_, name)
            print Fore.LIGHTBLUE_EX + "\tDownloading file", Fore.WHITE + name,
            print Fore.LIGHTBLUE_EX + "  ( of )",
            urllib.urlretrieve("http://resources.download.minecraft.net/{}/{}".format(hp, hash), pth,
                               create_urllib_reporthook(name))
            pth = os.path.join(cache_, os.path.dirname(name))
            if not os.path.exists(pth):
                os.makedirs(pth)
            pth = os.path.join(dir_, name)
            shutil.copy(pth, os.path.join(cache_, name))
            global prgrs
            prgrs = 0
            print "\033[2K\r\t" + Fore.LIGHTBLUE_EX + "Downloaded file", Fore.WHITE + name

    def get_textures(self, dir_, cache_):
        print Fore.GREEN + "Downloading and extracting assets from jar for", Fore.WHITE + self.ver
        url = "http://s3.amazonaws.com/Minecraft.Download/versions/{0}/{0}.jar".format(self.ver)
        f = zipfile.ZipFile(cache.cache_get(url))
        for i in f.namelist():
            if i.startswith("assets/"):
                print Fore.LIGHTBLUE_EX + "\tExtracting", Fore.WHITE + i,
                f.extract(i, dir_)
                f.extract(i, cache_)
                print "\r" + Fore.LIGHTBLUE_EX + "\tExtracted", Fore.WHITE + i

    def filter_unused(self, dir_, cache_, keep_realms=False, keep_icons=False):
        print Fore.GREEN + "Cleaning up unneeded files"
        delete_list = [
            "assets/skins", "assets/pack.mcmeta"
        ]
        if not keep_realms:
            delete_list.append("assets/realms")
        if not keep_icons:
            delete_list.append("assets/icons")
        delete_list = [os.path.join(dir_, x) for x in delete_list]
        delete_list_2 = [os.path.join(cache_, x) for x in delete_list]
        for i, j in zip(delete_list, delete_list_2):
            print "\t" + Fore.LIGHTBLUE_EX + "Deleting " + Fore.WHITE + i,
            try:
                if os.path.isfile(i):
                    os.remove(i)
                    os.remove(j)
                else:
                    shutil.rmtree(i)
                    shutil.rmtree(j)
            except:
                pass
            print "\r" + Fore.LIGHTBLUE_EX + "\tDeleted " + Fore.WHITE + i + "     "

    def get_all(self, dir_, cache_):
        self.get_assets(dir_, cache_)
        self.get_textures(dir_, cache_)


def grab_json(url):
    f = urllib.urlopen(url)
    return json.loads(f.read())


def get_mc_versions(quiet=False):
    if not quiet: print Fore.GREEN + "Downloading minecraft version list"
    versions = grab_json("http://s3.amazonaws.com/Minecraft.Download/versions/versions.json")["versions"]
    rl = {}
    for version in versions:
        if version["type"] not in ["snapshot", "release"]: continue
        rl[version["id"]] = MCVersion(version)
    return rl


def get_latest_mc_version(type):
    versions = grab_json("http://s3.amazonaws.com/Minecraft.Download/versions/versions.json")
    return versions["latest"][type]
