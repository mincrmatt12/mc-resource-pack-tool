import os

from colorama import init
import argparse

import lang
import project
import sound

init()

parser = argparse.ArgumentParser(prog="mcrsrctool")
subparsers = parser.add_subparsers(help="action")

parser_create = subparsers.add_parser('create', help="Create a new project")
parser_create.add_argument("-p", "--path", help="path to create project in, defaults to current directory",
                           default=os.getcwd())
parser_create.set_defaults(func=project.create_project)

parser_addsound = subparsers.add_parser('addsoundgroup', help="Add/Modify/Delete sound groups")
parser_addsound.add_argument("group", help="Name of sound group")
parser_addsound.add_argument("-c", "--category", help="Category of sound group", default="")
parser_addsound.add_argument("-r", "--remove", help="Add this to remove the sound group", action="store_true")
parser_addsound.set_defaults(func=sound.add_sound_group)

parser_astg = subparsers.add_parser('addsoundtogroup', help="Add/Modify/Delete sounds in groups")
parser_astg.add_argument("group", help="Name of sound group")
parser_astg.add_argument("sound", help="Path to sound file, relative to assets/minecraft/sounds")
parser_astg.add_argument("-r", "--remove", help="Add this to remove the sound from the group", action="store_true")
parser_astg.add_argument("-w", "--weight", help="Weight of the sound", default=1.0, type=float)
parser_astg.add_argument("-p", "--pitch", help="Pitch of the sound", default=1.0, type=float)
parser_astg.add_argument("-v", "--volume", help="Volume of the sound", default=1.0, type=float)
parser_astg.add_argument("-t", "--type", help="Type of the sound", default="sound", type=str,
                             choices=["sound", "event"])
parser_astg.add_argument("-s", "--stream", help="Whether to stream the sound", default=False, action="store_true")
parser_astg.set_defaults(func=sound.add_to_sound_group)

parser_addlang = subparsers.add_parser('addlanguage', help="Add/Modify/Delete languages")
parser_addlang.add_argument("file", help="Path to language file, relative to assets/minecraft/lang")
parser_addlang.add_argument("-r", "--remove", action="store_true", default=False, help="Delete the language")
parser_addlang.add_argument("-n", "--name", default=None, help="Name of language. If missing you will be asked")
parser_addlang.add_argument("--region", default=None, help="Region of language. If missing you will be asked")
parser_addlang.add_argument("--rtl", action="store_true", help="Set language as right-to-left")
parser_addlang.set_defaults(func=lang.add_language)

parser_refresh = subparsers.add_parser('refreshassets', help="Search and add assets such as sounds and languages automatically")
parser_refresh.add_argument("--nosound", action="store_false", help="Skip the refreshing of sound", dest="refresh_sound")
parser_refresh.add_argument("--nolang", action="store_false", help="Skip the refreshing of languages", dest="refresh_lang")
parser_refresh.add_argument("--manual", action="store_false", help="Enter all values in manually", dest="auto")
parser_refresh.set_defaults(func=project.refresh_assets)

parser_build = subparsers.add_parser('build', help="Build the assets into a zip")
parser_build.set_defaults(func=project.build)

args = parser.parse_args()
args.func(args)
