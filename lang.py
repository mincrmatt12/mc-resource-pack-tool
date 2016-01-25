import argparse
import json
import os
import input as input_

import project
from colorama import Fore


def is_lang_in_registry(file_):
    location = project.get_project_dir(os.getcwd(), ".mcrsrctools/metadata.json")

    entry_name = os.path.split(file_)[1]
    with open(location) as f:
        data = json.load(f)
        if entry_name in data["langs"]:
            return True
    return False


def refresh_file(file_):
    if input_.get_yn(Fore.LIGHTBLUE_EX + "Do you want to add " + Fore.WHITE + " " + file_ + Fore.LIGHTBLUE_EX + " to the list of languages (It will not be usable in-game unless you do so) " + Fore.CYAN):
        add_language(argparse.Namespace(remove=False, file=file_, name=None, region=None, rtl=False))
        return True
    return False


def add_language(args):
    json_pth = project.get_project_dir(os.getcwd(), ".mcrsrctools/metadata.json")
    json_dta = json.load(open(json_pth))

    real_path = project.get_project_dir(os.getcwd(), "assets/minecraft/lang")

    if not os.path.exists(os.path.join(real_path, args.file)):
        if input_.get_yn(Fore.RED + "Could not find specified lang file. Continue? " + Fore.CYAN) is False:
            return

    if args.remove:
        if args.file in json_dta["langs"]:
            del json_dta["langs"][args.file]
            print Fore.GREEN + "Deleted language " + Fore.WHITE + " " + args.file + Fore.GREEN + " successfully!"
        else:
            print Fore.RED + "Language does not exist"
    else:
        if args.file in json_dta["langs"]:
            print Fore.GREEN + "Collecting required info to modify language " + Fore.WHITE + " " + args.file
            name = args.name if args.name else raw_input(Fore.LIGHTBLUE_EX + "\tFull name of language: " + Fore.CYAN)
            region = args.region if args.region else raw_input(Fore.LIGHTBLUE_EX + "\tRegion of language: " + Fore.CYAN)
            rtl = args.rtl
            json_dta["langs"][args.file] = {"region": region, "rtl": rtl, "name": name}
            print Fore.GREEN + "Modified language " + Fore.WHITE + " " + args.file + Fore.GREEN + " successfully!"
        else:
            print Fore.GREEN + "Collecting required info to add language " + Fore.WHITE + " " + args.file
            name = args.name if args.name else raw_input(Fore.LIGHTBLUE_EX + "\tFull name of language: " + Fore.CYAN)
            region = args.region if args.region else raw_input(Fore.LIGHTBLUE_EX + "\tRegion of language: " + Fore.CYAN)
            rtl = args.rtl
            json_dta["langs"][args.file] = {"region": region, "rtl": rtl, "name": name}
            print Fore.GREEN + "Added language " + Fore.WHITE + " " + args.file + Fore.GREEN + " successfully!"
    json.dump(json_dta, open(json_pth, "w"))
