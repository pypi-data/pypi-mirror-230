import os
from subprocess import STDOUT, check_call


def install_python38():
    check_call(
        ["sudo apt-get update -y"],
        shell=True,
        stdin=None,
        stdout=open(os.devnull, "wb"),
        stderr=STDOUT,
        executable="/bin/bash",
    )
    check_call(
        ["sudo apt-get install python3.8"],
        shell=True,
        stdin=None,
        stdout=open(os.devnull, "wb"),
        stderr=STDOUT,
        executable="/bin/bash",
    )
    check_call(
        [
            "sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 4"
        ],
        shell=True,
        stdin=None,
        stdout=open(os.devnull, "wb"),
        stderr=STDOUT,
        executable="/bin/bash",
    )
    check_call(
        ["sudo apt install python3-pip"],
        shell=True,
        stdin=None,
        stdout=open(os.devnull, "wb"),
        stderr=STDOUT,
        executable="/bin/bash",
    )
    check_call(
        ["curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"],
        shell=True,
        stdin=None,
        stdout=open(os.devnull, "wb"),
        stderr=STDOUT,
        executable="/bin/bash",
    )
    check_call(
        ["python3 get-pip.py --force-reinstall"],
        shell=True,
        stdin=None,
        stdout=open(os.devnull, "wb"),
        stderr=STDOUT,
        executable="/bin/bash",
    )
