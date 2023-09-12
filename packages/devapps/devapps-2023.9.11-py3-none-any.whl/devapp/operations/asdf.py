"""
Default installation of asdf

=> Only req: . ~/.asdf/asdf.sh


FS changes: ~/.asdf

Requires: git, curl
"""

from devapp.tools import offset_port, exists, project
import os
import platform
from devapp.app import app, system
from devapp.tools import download_file, write_file, abspath, read_file
import json
from . import tools_help


def verify_present(path, rsc, **kw):
    return exists(path + '/asdf')


INST = 'git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.12.0'
ENVIRON_FILE = """
test -e bin/asdf && { . $HOME/.asdf/asdf.sh && asdf list; }
"""


H = os.environ['HOME']


def asdf(rsc, **kw):
    system('type git')
    system('type curl')
    if not exists(H + '/.asdf'):
        system(INST)
        system(f'. "{H}/.asdf/asdf.sh" && asdf plugin list all')

    # def r(i):
    #     d = R + '/bin/.binenv'
    #     return abspath(os.environ.get(f'binenv_{i}dir', d))
    #
    # envs = [r(i) for i in ['bin', 'link', 'cache', 'config']]
    # pre = T.format(envs=envs)

    pre = '. "$HOME/.asdf/asdf.sh"\n'
    tools_help.write_environ(ENVIRON_FILE, match='asdf')
    tools_help.write_tools_cmd()
    return {'cmd': ':asdf', 'cmd_pre': pre}


class asdf:
    """*FAST* installed version managed binary resources"""

    verify_present = verify_present
    pkg = False
    cmd = asdf
