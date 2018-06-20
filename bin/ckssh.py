#!/usr/bin/env python3

from argparse       import ArgumentParser
from collections    import namedtuple as ntup
from os             import path
from pathlib        import Path
from subprocess     import call
from sys            import stdout, stderr
import os, re, sys

############################################################
#   Defaults

CONFIG_FILE = '~/.ssh/ckssh_config'
devnull = open(os.devnull, 'w')

############################################################
#   Functions

def parseconfig(config):
    parser = re.compile(r'(?:\s*)(\w+)(?:\s*=\s*|\s+)(.+)')
    compartments = []
    current = None
    for line in config:
        match = parser.match(line)
        if not match: continue

        key = match.group(1).lower()
        value = match.group(2)
        if key == 'ck_host':
            current = None
        if key == 'ck_compartment':
            current = CK.CompartmentConfig(name=value, keyfiles=[])
            compartments.append(current)
        if key == 'ck_keyfile':
            if current:
                current.keyfiles.append(value)
            else:
                raise RuntimeError('Got keyfile without compartment')

    return compartments

def runtimedir(env=os.environ):
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

class CK:
    #   Default socket path to use when not specified
    SOCK = os.environ.get('SSH_AUTH_SOCK')

    CompartmentConfig = ntup('CompartmentConfig', 'name,keyfiles')
    class UnknownCompartment: pass

    def __init__(self, configfile=None, compartment_path=runtimedir()):
        self.configfile = configfile or os.path.expanduser(CONFIG_FILE)
        self.compartment_path = Path(compartment_path)
        self.compartments = []
        with open(str(self.configfile)) as f:
            self.compartments = parseconfig(f)

    def sockpath(self, name):
        return Path(self.compartment_path, 'socket', name)

    def compartment_from_sock(self, ssh_auth_sock=SOCK):
        if not ssh_auth_sock:
            return None
        for c in self.compartments:
            if str(self.sockpath(c.name)) == str(ssh_auth_sock):
                return c
        return self.UnknownCompartment


EVALFILE = stdout

def evalwrite(s):
    EVALFILE.write(s)
    EVALFILE.write('\n')

def print_bash_init(_):
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

def shell_interface_test(_):
    print('stdout')
    print('stderr', file=stderr)
    evalwrite('echo evaled;')
    evalwrite('export CKSSH_SHELL_INTERFACE_TEST=1;')

def ckset(args):
    if args.params:
        print('Bad args: {}'.format(args.params), file=stderr)
        return 2

    ck = CK()
    compartment = ck.compartment_from_sock()
    if compartment == None:
        print('No compartment.', file=stderr)
        return 1
    elif compartment == CK.UnknownCompartment:
        print('Unknown compartment.', file=stderr)
        if args.a:
            return 1    # We don't know a list of keys for this compartment.
    else:
        print(compartment.name)
        if args.a:
            exitcode = 0
            for keyfile in compartment.keyfiles:
                (dir, file) = path.split(keyfile)
                e = call(['ssh-add', file], cwd=path.expanduser(dir))
                if exitcode == 0: exitcode = e

    #   We need to check to see if the compartment is running and
    #   return 0 in that case.
    e = call(['ssh-add', '-l'], stdin=devnull, stdout=devnull, stderr=devnull)
    if e == 2:
        return 2
    return 0


############################################################
#   Main

def main():
    global CONFIG_FILE, EVALFILE

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
    arg('subcommand', help=' '.join(sorted(subcommands.keys())))
    arg('params', nargs='*')
    args = p.parse_args()

    CONFIG_FILE = args.config_file
    if args.eval_file:  EVALFILE = open(args.eval_file, 'wt')

    #   This is not really the right way to do subcommands; we should be using
    #   https://docs.python.org/3/library/argparse.html#sub-commands
    sys.exit(subcommands[args.subcommand](args))

if __name__ == '__main__': main()
