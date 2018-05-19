#!/usr/bin/env python

from argparse import ArgumentParser
from collections import namedtuple as ntup
from sys import stdout, stderr
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
        self.compartment_path = compartment_path
        with open(str(self.configfile)) as f:
            self.compartments = parseconfig(f)

    def get_compartment(self, ssh_auth_sock):
        return None


EVALFILE = stdout

def evalwrite(s):
    EVALFILE.write(s)
    EVALFILE.write('\n')
    
def print_bash_init():
    evalwrite('''
        ckset() {
            local retval=0;
            local evalfile=$(mktemp -t ckssh-eval-XXXXX);
            ckssh.py --eval-file "$evalfile" "$@"; retval=$?;
            eval $(cat "$evalfile");
            rm -f "$evalfile";
            return $retval;
        }
    ''')

def proof_of_concept():
    print('stdout')
    print('stderr', file=stderr)
    evalwrite('echo evaled;')
    evalwrite('export CKSSH_PROOF_OF_CONCEPT=1;')

def main():
    p = ArgumentParser(description='Comparmentalized Key Agents for SSH')
    arg = p.add_argument
    arg('--bash-init', action='store_true',
        help='Print code to configure Bash with ckssh commands')
    arg('--eval-file')
    arg('--proof-of-concept', action='store_true')
    args = p.parse_args()

    if args.eval_file:
        global EVALFILE
        EVALFILE = open(args.eval_file, 'wt')
    if args.proof_of_concept:
        proof_of_concept()
        exit(0)
    if args.bash_init:
        print_bash_init()
        exit(0)

if __name__ == '__main__': main()
