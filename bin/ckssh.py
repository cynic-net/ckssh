#!/usr/bin/env python3

from argparse       import ArgumentParser
from collections    import namedtuple as ntup
from pathlib        import Path
from sys            import stdout, stderr
import re


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
