import argparse
import copy
import json
import os

from colorama import Fore

import input as input_

import project


def create_soundjson(oldfile, editedfile, newfile):
    a = json.load(open(oldfile))
    b = json.load(open(editedfile))
    json.dump(scan_for_diffs(a, b), open(newfile, "w"), indent=4)


def scan_for_diffs(default, created):
    merged = {}
    for sound in created:
        if sound in default:
            old = default[sound]
            new = created[sound]
            if old == new:
                continue
            else:
                merged[sound] = new
                merged[sound]["replace"] = True
        else:
            merged[sound] = created[sound]
    return merged


def is_in_sound_group(file_):
    location = project.get_project_dir(join="assets/minecraft/sounds.json")

    file_entry_pos = os.path.splitext(
        os.path.relpath(file_, os.path.normpath(project.get_project_dir(join="assets/minecraft/sounds"))).replace(
            os.path.sep, '/'))[0]

    with open(location, "r+") as f:
        sounds = json.load(f)
        for sound in sounds:
            for other_sound in sounds[sound]["sounds"]:
                if type(other_sound) == unicode:
                    if other_sound == file_entry_pos:
                        return True
                else:
                    if other_sound["name"] == file_entry_pos:
                        return True
        return False


def refresh_sound(file_):
    choice = input_.options_retnum(
        Fore.LIGHTBLUE_EX + "What do you want to do with " + Fore.WHITE + " " + file_ + "? " + Fore.CYAN, [
                "Create a new sound group and add the file to it",
                "Add the file to an existing sound group",
                "Ignore it completely (you will not be able to use it in-game)"
            ])
    if choice == 0:
        group_name = raw_input(Fore.LIGHTBLUE_EX + "What shall I call the new sound group? " + Fore.CYAN)
        add_sound_group(argparse.Namespace(category="", group=group_name, remove=False))
    if choice == 1:
        group_name = raw_input(Fore.LIGHTBLUE_EX + "To which group should I add this sound? " + Fore.CYAN)
    if choice in (0, 1):
        print Fore.LIGHTBLUE_EX + "Leave any option blank for default"
        weight = input_.defaulted_in(Fore.LIGHTBLUE_EX + "Sound weight? " + Fore.CYAN, 1.0, float)
        pitch = input_.defaulted_in(Fore.LIGHTBLUE_EX + "Sound pitch? " + Fore.CYAN, 1.0, float)
        volume = input_.defaulted_in(Fore.LIGHTBLUE_EX + "Sound volume? " + Fore.CYAN, 1.0, float)
        type = input_.options(Fore.LIGHTBLUE_EX + "Sound type? (use 0 for default)", ["sound", "event"])
        stream = input_.get_yn(Fore.LIGHTBLUE_EX + "Stream sound (default is N) ")
        add_to_sound_group(
            argparse.Namespace(group=group_name, weight=weight, pitch=pitch, volume=volume, type=type, stream=stream,
                               sound=file_, remove=False))
    elif choice == 2:
        return False
    return True


def add_sound_group(args):
    if project.get_project_dir(os.getcwd()):
        proj_json = json.load(open(os.path.join(project.get_project_dir(os.getcwd()), "assets/minecraft/sounds.json")))
        if args.group not in proj_json:
            new_group = {}
            category = args.category
            if args.category == "":
                category = input_.options(Fore.LIGHTBLUE_EX + "Please select a category:", [
                    "master", "ambient", "weather", "player", "neutral", "hostile", "block", "record", "music"
                ])
            new_group["category"] = category
            new_group["sounds"] = []
            proj_json[args.group] = new_group
            if args.remove:
                del proj_json[args.group]
            json.dump(proj_json,
                      open(os.path.join(project.get_project_dir(os.getcwd()), "assets/minecraft/sounds.json"), "w"),
                      indent=4)
            if not args.remove:
                print Fore.GREEN + "Added sound group " + Fore.WHITE + args.group + Fore.GREEN + " successfully!"
            else:
                print Fore.GREEN + "Removed sound group " + Fore.WHITE + args.group + Fore.GREEN + " successfully!"
        else:
            if args.remove:
                del proj_json[args.group]
                json.dump(proj_json,
                          open(os.path.join(project.get_project_dir(os.getcwd()), "assets/minecraft/sounds.json"), "w"),
                          indent=4)
                print Fore.GREEN + "Removed sound group " + Fore.WHITE + args.group + Fore.GREEN + " successfully!"
                return
            print Fore.RED + "Sound group already exists!" + Fore.CYAN + \
                  " (maybe you wanted mcrsrctool addsoundtogroup?)"
    else:
        print Fore.RED + "Could not find project"


def add_to_sound_group(args):
    if project.get_project_dir(os.getcwd()):
        proj_json = json.load(open(os.path.join(project.get_project_dir(os.getcwd()), "assets/minecraft/sounds.json")))
        if args.group not in proj_json:
            print Fore.RED + "Sound group does not exist! " + Fore.CYAN + "(maybe you wanted mcrsrctool addsoundgroup?)"
        else:
            if not os.path.exists(
                    os.path.join(os.path.join(project.get_project_dir(os.getcwd()), "assets/minecraft/sounds"),
                                 args.sound)):
                if not input_.get_yn(
                                        Fore.RED + "I couldn't find the specified sound. Continue anyways? [Y or N] " + Fore.CYAN):
                    return
            args.sound = os.path.splitext(args.sound)[0]
            group = proj_json[args.group]
            new_s = []

            for entry in group["sounds"]:
                # print type(entry)
                if type(entry) == unicode:
                    if entry == args.sound:
                        ##        print "conting"
                        continue
                else:
                    if entry["name"] == args.sound:
                        ##          print "conting"
                        continue
                new_s.append(entry)
            ##print new_s
            data = {"name": args.sound}
            us = True
            if args.type == "event":
                data["type"] = "event"
                us = False
            if args.volume != 1.0:
                data["volume"] = args.volume
                us = False
            if args.pitch != 1.0:
                data["pitch"] = args.pitch
                us = False
            if args.weight != 1.0:
                data["weight"] = args.weight
                us = False
            if args.stream:
                data["stream"] = True
                us = False
            if us:
                data = args.sound
            if not args.remove: new_s.append(data)
            proj_json[args.group]["sounds"] = new_s
            json.dump(proj_json,
                      open(os.path.join(project.get_project_dir(os.getcwd()), "assets/minecraft/sounds.json"), "w"),
                      indent=4)
            if not args.remove:
                print Fore.GREEN + "Added sound " + Fore.WHITE + args.sound + Fore.GREEN + " to group " + Fore.WHITE \
                      + args.group + Fore.GREEN + " successfully!"
            else:
                print Fore.GREEN + "Removed sound " + Fore.WHITE + args.sound + Fore.GREEN + " from group " + Fore.WHITE \
                      + args.group + Fore.GREEN + " successfully!"

    else:
        print Fore.RED + "Could not find project"
