#!/usr/bin/env python

from argparse import ArgumentParser

def print_bash_init():
    print('ckset() { true; }')

def main():
    p = ArgumentParser(description='Comparmentalized Key Agents for SSH')
    arg = p.add_argument
    arg('--bash-init', action='store_true',
        help='Print code to configure Bash with ckssh commands')
    args = p.parse_args()
    if args.bash_init:
        print_bash_init()
        exit(0)

if __name__ == '__main__': main()
