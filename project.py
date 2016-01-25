import argparse
import ctypes
import filecmp
import json
import os
import shutil

import sys
from colorama import Fore

import download
import lang
import sound
from input import get_yn


def create_project(args):
    dir_ = args.path
    print Fore.GREEN + "Creating new project in", Fore.WHITE + dir_
    path_to_info_dir = os.path.join(dir_, ".mcrsrctools")
    os.makedirs(path_to_info_dir)
    if os.name == "nt":
        ctypes.windll.kernel32.SetFileAttributesW(unicode(os.path.abspath(path_to_info_dir)), 0x02)
    print Fore.GREEN + "Collecting info for resource pack"
    print Fore.LIGHTBLUE_EX + "\tPack name:" + Fore.CYAN,
    name = raw_input()
    print Fore.LIGHTBLUE_EX + "\tPack description:" + Fore.CYAN,
    desc = raw_input()
    mc_versions = download.get_mc_versions()
    print Fore.LIGHTBLUE_EX + "\tMC version options:\n"
    print Fore.RED + "[0]", Fore.LIGHTBLUE_EX + "Use latest release\n"
    print Fore.RED + "[1]", Fore.LIGHTBLUE_EX + "Use latest snapshot\n"
    print Fore.RED + "[2]", Fore.LIGHTBLUE_EX + "Let me pick from the list\n"
    pick = -1
    while pick == -1:
        try:
            print Fore.LIGHTBLUE_EX + "Please select an option: " + Fore.CYAN,
            pick = int(raw_input())
            if pick < 0 or pick > 2:
                print Fore.RED + "Invalid option"
                pick = -1
        except:
            pick = -1
            print Fore.RED + "Not a number"
    version = None
    if pick == 0:
        version = mc_versions[download.get_latest_mc_version("release")]
    elif pick == 1:
        version = mc_versions[download.get_latest_mc_version("snapshot")]
    else:
        print Fore.LIGHTBLUE_EX + "Available versions:"
        for i in mc_versions.keys():
            print Fore.WHITE + i
        vv = None
        while vv is None:
            print Fore.LIGHTBLUE_EX + "Version: " + Fore.CYAN,
            v = raw_input()
            if v in mc_versions:
                vv = mc_versions[v]
            else:
                print Fore.RED + "Invalid version"
        version = vv
    i_ = ""
    while i_ == "":
        print Fore.LIGHTBLUE_EX + "Do you want to download default minecraft assets (you need to do this once before you pack your resource pack) [Y or N]:" + Fore.CYAN,
        a = raw_input().lower()
        if a not in ["y", "n"]:
            continue
        i_ = a

    assetsdownloaded = i_ == "y"
    if i_ == "y":
        kr = get_yn(Fore.LIGHTBLUE_EX + "Do you need realms assets [Y or N]: " + Fore.CYAN)
        ki = get_yn(Fore.LIGHTBLUE_EX + "Do you want icons [Y or N]: " + Fore.CYAN)
        version.get_all(dir_, os.path.join(path_to_info_dir, "default_files"))
        version.filter_unused(dir_, os.path.join(path_to_info_dir, "default_files"), kr, ki)
    store = {
        "name": name,
        "desc": desc,
        "mc_version": version.ver,
        "assets_grabbed": assetsdownloaded,
        "has_realms": kr,
        "has_icons": ki,
        "langs": {}
    }
    json.dump(store, open(os.path.join(path_to_info_dir, "metadata.json"), "w"))


def get_project_dir(cwd=None, join=""):
    found = False
    path = cwd if cwd else os.getcwd()
    while not found and os.path.dirname(path) != path:
        if os.path.exists(os.path.join(path, ".mcrsrctools")):
            if os.path.isdir(os.path.join(path, ".mcrsrctools")):
                return os.path.join(path, join)
        path = os.path.dirname(path)
    print Fore.RED + "Not in a project directory"
    sys.exit(0)


def run_refresh():
    refresh_assets(argparse.Namespace(refresh_sound=True, refresh_lang=True))


def refresh_assets(args):
    if args.refresh_sound:
        sound_dir = get_project_dir(join="assets/minecraft/sounds")
        sound_dir2 = get_project_dir(join=".mcrsrctools/default_files/assets/minecraft/sounds")
        print Fore.GREEN + "Scanning for unused sounds"
        for (root, dirs, files) in os.walk(sound_dir):
            print "\033[2K\r" + Fore.LIGHTBLUE_EX + "\tScanning directory " + Fore.WHITE + root,
            for file_ in files:
                full = os.path.join(root, file_)
                relative = os.path.normpath(os.path.relpath(full, sound_dir)).replace(os.path.sep, '/')
                default_path = os.path.join(sound_dir2, relative)
                if not os.path.exists(default_path):
                    if not sound.is_in_sound_group(full):
                        print "\033[2K"
                        sound.refresh_sound(relative)
        print "\033[2K\r" + Fore.GREEN + "Done scanning sounds"
    if args.refresh_lang:
        lang_dir = get_project_dir(join="assets/minecraft/lang")
        lang_dir2 = get_project_dir(join=".mcrsrctools/default_files/assets/minecraft/lang")
        print Fore.GREEN + "Scanning for unused languages"
        for file_ in os.listdir(lang_dir):
            print "\033[2K\r" + Fore.LIGHTBLUE_EX + "\tChecking file " + Fore.WHITE + file_,
            test_path = os.path.join(lang_dir2, file_)
            if not os.path.exists(test_path):
                if not lang.is_lang_in_registry(os.path.join(lang_dir, file_)):
                    print "\033[2K"
                    lang.refresh_file(file_)
        print "\033[2K\r" + Fore.GREEN + "Done scanning languages"

SKIP_COPY = False


def build(args):
    project_directory = get_project_dir()
    metadata = json.load(open(os.path.join(project_directory, ".mcrsrctools/metadata.json")))
    print Fore.GREEN + "Building resource pack " + Fore.WHITE + " " + metadata["name"]
    print Fore.GREEN + "Running refresh assets"
    run_refresh()
    print Fore.GREEN + "Copying assets to build dir"
    build_dir = os.path.join(project_directory, ".mcrsrctools/build/assets")
    default_dir = os.path.join(project_directory, ".mcrsrctools/default_files/assets")
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
        print Fore.LIGHTBLUE_EX + "\tMade build dir"
    if not SKIP_COPY:
        for root, dirs, files in os.walk(os.path.join(project_directory, "assets"), topdown=False):
            isolated = os.path.relpath(root, os.path.join(project_directory, "assets"))
            if not os.path.exists(os.path.join(build_dir, isolated)):
                os.makedirs(os.path.join(build_dir, isolated))
                print Fore.LIGHTBLUE_EX + "\tCreated directory " + Fore.WHITE + " " + isolated
            for file_ in files:
                shutil.copy(os.path.join(root, file_), os.path.join(build_dir, isolated, file_))
                print Fore.LIGHTBLUE_EX + "\tCopied " + Fore.WHITE + " " + os.path.join(root, file_)
    print Fore.GREEN + "Deleting unnecessary assets"
    for root, dirs, files in os.walk(build_dir):
        print "\033[2K\r\t" + Fore.LIGHTBLUE_EX + "Checking directory " + Fore.WHITE + 
       # print root, dirs, files
        for file_ in files:
           # print os.path.join(default_dir, root, file_)
            #print default_dir, root
            if not os.path.exists(os.path.join(default_dir, os.path.relpath(root, build_dir), file_)):
               # print "skipping"
                continue
            if filecmp.cmp(os.path.join(build_dir, root, file_), os.path.join(default_dir, os.path.relpath(root, build_dir), file_), 0):
                #print "removing " + os.path.join(build_dir, root, file_)
                os.remove(os.path.join(build_dir, root, file_))