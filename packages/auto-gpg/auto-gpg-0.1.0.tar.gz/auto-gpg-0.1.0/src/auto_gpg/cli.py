import os
import shutil

from os import path


def main():
    # working directory
    cwd = path.abspath(os.getcwd())

    home = None

    # open configuration file
    with open(path.expanduser("~/.auto-gpg")) as f:
        for line in f.readlines():
            line = line.strip()
            # blank or comment
            if line == "" or line.startswith("#"):
                continue
            # decode line
            splits = line.split(":", 1)
            if len(splits) != 2:
                print('auto-gpg: found invalid line "'+line+'" in ~/.auto-gpg')
                continue
            # check if cwd is in dir
            dir = path.abspath(path.expanduser(splits[0]))
            if cwd.startswith(dir):
                home = path.abspath(path.expanduser(splits[1]))
                break

    # set GNUPGHOME
    if home is None:
        print("auto-gpg: no GNUPGHOME rule found for "+cwd)
    else:
        print("auto-gpg: setting GNUPGHOME to "+home)
        os.putenv("GNUPGHOME", home)

    # find gpg command
    gpg = shutil.which("gpg")

    if gpg is None:
        raise Exception("gpg not found")

    # run gpg with exec syscall
    os.execl(gpg, "gpg", *os.sys.argv[1:])


if __name__ == "__main__":
    main()
