import os
from devapp.tools import read_file, write_file, project
from devapp.app import app


def write_environ(body, match):
    fn = project.root() + '/environ'
    s = read_file(fn, dflt='')
    s = '\n'.join([l for l in s.splitlines() if not match in l.lower()])
    s += body
    write_file(fn, s)


T = ''


def write_tools_cmd():
    return
    app.info('Generating tools command')
    write_file(project.root() + '/bin/tools', T, chmod=0o755)
