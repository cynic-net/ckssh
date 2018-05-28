#!/usr/bin/env python3

from argparse       import ArgumentParser
from collections    import namedtuple as ntup
from pathlib        import Path
from sys            import stdout, stderr
import os, re


CompartmentConfig = ntup('CompartmentConfig', 'name')

def parseconfig(config):
    parser = re.compile(r'(?:\s*)(\w+)(?:\s*=\s*|\s+)(.+)')
    compartments = []
    for line in config:
        match = parser.match(line)
        if not match: continue
        key = match.group(1).lower()
        value = match.group(2)
        if key == 'ck_compartment':
            compartments.append(CompartmentConfig(name=value))
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
    def __init__(self, configfile=None, compartment_path=None):
        self.configfile = configfile
        self.compartment_path = Path(compartment_path)
        if configfile:
            with open(str(self.configfile)) as f:
                self.compartments = parseconfig(f)

    def sockpath(self, name):
        return Path(self.compartment_path, 'socket', name)

    def get_compartment(self, ssh_auth_sock):
        for c in self.compartments:
            print(c, self.sockpath(c.name), ssh_auth_sock)
            if str(self.sockpath(c.name)) == str(ssh_auth_sock):
                return c.name
        return None


EVALFILE = stdout

def evalwrite(s):
    EVALFILE.write(s)
    EVALFILE.write('\n')

def print_bash_init():
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

def test_shell_interface():
    print('stdout')
    print('stderr', file=stderr)
    evalwrite('echo evaled;')
    evalwrite('export CKSSH_TEST_SHELL_INTERFACE=1;')

def main():
    subcommands = {
        'bash-init':            print_bash_init,
        'test-shell-interface': test_shell_interface,
    }

    p = ArgumentParser(description='Comparmentalized Key Agents for SSH')
    arg = p.add_argument
    arg('--config-file', '-c')
    arg('--eval-file')
    arg('subcommand', help=' '.join(sorted(subcommands.keys())))
    arg('params', nargs='*')
    args = p.parse_args()

    if args.eval_file:
        global EVALFILE
        EVALFILE = open(args.eval_file, 'wt')

    #   This is not really the right way to do subcommands; we should be using
    #   https://docs.python.org/3/library/argparse.html#sub-commands
    subcommands[args.subcommand](*args.params)

if __name__ == '__main__': main()
