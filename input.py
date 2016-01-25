from colorama import Fore


def get_yn(prompt):
    val = None
    while val is None:
        print prompt,
        v = raw_input().lower()
        if v not in ("y", "n"):
            print Fore.RED + "Invalid input"
            continue
        val = v == "y"
    return val


def defaulted_in(prompt, default, type_):
    raw = raw_input(prompt)
    try:
        if raw == "":
            return default
        else:
            return type_(default)
    except:
        return default

def options(prompt, options):
    print prompt
    for i in options:
        print Fore.LIGHTBLUE_EX + "[{}]".format(options.index(i)), Fore.WHITE + i
    v = -1
    while v == -1:
        print Fore.LIGHTBLUE_EX + "Please select an option: ", Fore.CYAN,
        try:
            v = int(raw_input())
            if v > len(options) - 1 or v < 0:
                print Fore.RED + "Not an option"
                v = -1
        except:
            print Fore.RED + "Not a number"
            v = -1
    return options[v]

def options_retnum(prompt, options):
    print prompt
    for i in options:
        print Fore.LIGHTBLUE_EX + "[{}]".format(options.index(i)), Fore.WHITE + i
    v = -1
    while v == -1:
        print Fore.LIGHTBLUE_EX + "Please select an option: ", Fore.CYAN,
        try:
            v = int(raw_input())
            if v > len(options) - 1 or v < 0:
                print Fore.RED + "Not an option"
                v = -1
        except:
            print Fore.RED + "Not a number"
            v = -1
    return v
