#!/usr/bin/env python3

from argparse       import ArgumentParser
from collections    import namedtuple as ntup
from os             import path
from pathlib        import Path
from subprocess     import call
import os, re, sys

############################################################
#   Defaults

CONFIG_FILE     = '~/.ssh/ckssh_config'
DEVNULL         = open(os.devnull, 'w')

############################################################
#   Compartment classes and functions

def runtimedir(env):
    #   If envvar XDG_RUNTIME_DIR is set, we're set. However, in non-desktop
    #   environments (e.g., ssh login to a server) it's usually not set
    #   (and it's probably nonexistent on Windows, too). In that case
    #   for the moment, we just use `/run/user/{uid}` which will be there
    #   on modern (e.g., Ubuntu >= 14.04) Linux systems.
    #
    #   For other systems, the current workaround is for the user to set
    #   XDG_RUNTIME_DIR himself. In the long run we probably want to work
    #   out better fallback plans.
    #
    #   For more information on the XDG Base Directory Specification, see:
    #   https://specifications.freedesktop.org/basedir-spec/latest/
    xdg = env.get('XDG_RUNTIME_DIR')
    if xdg:
        return Path(xdg, 'ckssh')
    return Path('/run/user', str(os.getuid()), 'ckssh')

class Compartment(object):
    def __init__(self, name, keyfiles):
        self.name     = name
        self.keyfiles = keyfiles
        self.confirm  = True

def parseconfig(stream):
    parser = re.compile(r'(?:\s*)(\w+)(?:\s*=\s*|\s+)(.+)')
    compartments = []
    current = None
    for line in stream:
        match = parser.match(line)
        if not match: continue

        key = match.group(1).lower()
        value = match.group(2)
        if key == 'ck_host':
            current = None
        if key == 'ck_compartment':
            current = Compartment(name=value, keyfiles=[])
            compartments.append(current)
        if key == 'ck_keyfile':
            if current:
                current.keyfiles.append(value)
            else:
                raise RuntimeError('Got keyfile without compartment')
        if key == 'ck_confirm':
            if value == 'yes':
                value = True
            elif value == 'no':
                value = False
            else:
                raise RuntimeError('Invalid CK_confirm value: {}'.format(value))
            if current:
                current.confirm = value
            else:
                raise RuntimeError('Got CK_confirm without compartment')

    return compartments

class CK:
    class UnknownCompartment: pass

    def __init__(self, env, *, configfile=None, compartment_path=None):
        self.env = env
        #   This hack is needed to make expanduser() use our env
        os.environ['HOME'] = env.get('HOME', os.environ.get('HOME'))
        self.configfile = configfile or os.path.expanduser(CONFIG_FILE)
        if compartment_path:
            self.compartment_path = Path(compartment_path)
        else:
            self.compartment_path = Path(runtimedir(env))
        self.default_sock = env.get('SSH_AUTH_SOCK')
        self.compartments = []
        with open(str(self.configfile)) as f:
            self.compartments = parseconfig(f)

    def sockpath(self, name):
        return Path(self.compartment_path, 'socket', name)

    def compartment_from_sock(self, ssh_auth_sock=None):
        if not ssh_auth_sock:
            ssh_auth_sock = self.default_sock
        if not ssh_auth_sock:
            return None
        for c in self.compartments:
            if str(self.sockpath(c.name)) == str(ssh_auth_sock):
                return c
        return self.UnknownCompartment

############################################################
#   Program operation classes and functions

EVALFILE = sys.stdout

def evalwrite(s):
    EVALFILE.write(s)
    EVALFILE.write('\n')

def print_bash_init(_args, _env):
    me = str(Path(__file__).resolve())
    evalwrite('''
        ckcommand() {
            local retval=0;
            local evalfile=$(mktemp -t ckssh-eval-XXXXX);
            ''' + me + ''' --eval-file "$evalfile" "$@"; retval=$?;
            eval $(cat "$evalfile");
            rm -f "$evalfile";
            return $retval;
        };
        ckset() { ckcommand ckset "$@"; }
    ''')

def printerr(*args, **kwargs):
    print('ckssh:', *args, file=sys.stderr, **kwargs)

def shell_interface_test(_args, _env):
    print('stdout')
    printerr('stderr')
    evalwrite('echo evaled;')
    evalwrite('export CKSSH_SHELL_INTERFACE_TEST=1;')

def canexec(command):
    ' Return whether or not we can (probably) exec the given command. '
    #   `shutil.which` is only in Python ≥ 3.3
    #   This doesn't work on Windows, but perhaps `where` would do the trick?
    return 0 == call(['which', command], stdout=DEVNULL)

def addkeys(compartment):
    exitcode = 0
    for keyfile in compartment.keyfiles:
        (dir, file) = path.split(keyfile)
        args = ['ssh-add', '-t', '10h']
        if compartment.confirm:
            args += ['-c']
            if not canexec('ssh-askpass'):
                printerr('WARNING: ssh-askpass not available but needed for'
                    ' compartment {}'.format(compartment.name))
        args += [file]
        e = call(args, cwd=path.expanduser(dir))
        if exitcode == 0: exitcode = e
    return exitcode

def ckset(args, env):
    if args.params:
        printerr('Bad args: {}'.format(args.params))
        return 2

    ck = CK(env)
    compartment = ck.compartment_from_sock()
    if compartment == None:
        printerr('No compartment.')
        return 1
    elif compartment == CK.UnknownCompartment:
        printerr('Unknown compartment.')
        if args.a:
            return 1    # We don't know a list of keys for this compartment.
    else:
        print(compartment.name)
        if args.a:
            e = addkeys(compartment)
            if e != 0:
                return e

    #   Assuming no previous errors, we may have not yet queried the agent
    #   so check to see if the compartment is running (0) or not (2).
    e = call(['ssh-add', '-l'], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    if e == 2:
        return 2
    return 0


############################################################
#   Main

def argparser():
    subcommands = {
        'bash-init':            print_bash_init,
        'shell-interface-test': shell_interface_test,
        'ckset':                ckset,
    }
    p = ArgumentParser(description='Comparmentalized Key Agents for SSH')
    arg = p.add_argument
    arg('-a', action='store_true',
        help='Add all configured but unloaded keys to the compartment.')
    arg('-c', '--config-file', default=CONFIG_FILE,
        help='config file to use, default {}'.format(CONFIG_FILE))
    arg('--eval-file',
        help='file to which to write commands for parent shell')
    arg('-s', '--start', action='store_true',
        help='If necessary, start agent for compartment'
            ' (automatic when changing compartments)')
    arg('subcommand', help=' '.join(sorted(subcommands.keys())))
    arg('params', nargs='*')
    return p, subcommands

def main():
    global CONFIG_FILE, EVALFILE
    p, subcommands = argparser()
    args = p.parse_args()

    CONFIG_FILE = args.config_file
    if args.eval_file:  EVALFILE = open(args.eval_file, 'wt')

    #   This is not really the right way to do subcommands; we should be using
    #   https://docs.python.org/3/library/argparse.html#sub-commands
    sys.exit(subcommands[args.subcommand](args, os.environ))

if __name__ == '__main__': main()
