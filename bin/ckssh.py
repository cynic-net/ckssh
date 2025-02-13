#!/usr/bin/env python3

from argparse       import ArgumentParser
from binascii       import hexlify
from collections    import namedtuple as ntup
from os             import path
from pathlib        import Path
from subprocess     import call, DEVNULL
import os, re, socket, sys

############################################################
#   Defaults

CONFIG_FILE     = '~/.ssh/ckssh_config'
DEVNULL         = open(os.devnull, 'w')

############################################################
#   SSH agent protocol functions

class SSHAgentProtoError(RuntimeError):
    pass

def read_agentproto_int(stream, length):
    bs = stream.read(length)
    if len(bs) != length:
        raise SSHAgentProtoError(
            'Short int (expected {}): {}'.format(length, bs))
    return int.from_bytes(bs, byteorder='big')

def read_agentproto_bstr(stream):
    length = read_agentproto_int(stream, 4)
    bs = stream.read(length)
    if len(bs) != length:
        raise SSHAgentProtoError('Short string: {}'.format(bs))
    return bs

def read_agentproto_idcomments(stream):
    ''' From the given I/O stream, Read and parse an
        ``SSH2_AGENT_IDENTITIES_ANSWER`` response to an
        ``SSH2_AGENTC_REQUEST_IDENTITIES`` request.
        Return a list with the comment for each identity.

        For protocol details see section 2.5.2 of
        <http://api.libssh.org/rfc/PROTOCOL.agent>.
    '''
    #   We don't actually use the message length, instead relying on
    #   the count of keys and string lengths, but we parse it to make
    #   sure this isn't a bad message.
    msglen = read_agentproto_int(stream, 4)

    msgtype = read_agentproto_int(stream, 1)
    if msgtype != 0xC:
        raise SSHAgentProtoError(
            'Unknown message type: {}'.format(msgtype))

    keycount = read_agentproto_int(stream, 4)
    comments = []
    for i in range(0, keycount):
        read_agentproto_bstr(stream)             # key blob
        bs = read_agentproto_bstr(stream)        # key comment
        comments.append(bs.decode('ascii'))
    return comments

    raise SSHAgentProtoError()
    return []

def fetch_keynames(sockpath):
    ''' Connects to the given ssh-agent socket and returns a (possibly
        empty) list of the comments for the keys the agent is holding.
        Returns `None` if no agent is listening on that path.
    '''
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    if sockpath is None:
        sockpath = os.environ.get('SSH_AUTH_SOCK')
    try:
        sock.connect(bytes(sockpath))
    except (ConnectionRefusedError, FileNotFoundError):
        return None
    sock.sendall(b'\x00\x00\x00\x01'    # message length = 1
                 b'\x0b')               # SSH2_AGENTC_REQUEST_IDENTITIES
    #   !!! This shuts down both sides of the connection!
    #sock.shutdown(socket.SHUT_WR)
    comments = read_agentproto_idcomments(sock.makefile('rb'))
    sock.close()
    return comments

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
    ''' Parse a ckssh configuration file, returning a list of
        `Compartment` objects.
    '''
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
    ''' A ckssh configuration.

        This handles finding the config file, calling `parseconfig()`
        to load and parse it, and searching the resulting list of
        compartments.
    '''
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

    def sockpath(self, name=None):
        ''' Return the path to the socket for compartment `name`, if not
            `None`, otherwise the path to the default socket (the
            ``SSH_AUTH_SOCK`` environment variable).
        '''
        if name is None:
            return Path(self.default_sock)
        else:
            return Path(self.compartment_path, 'socket', name)

    def compartment_named(self, name):
        for c in self.compartments:
            if c.name == name:
                return c
        return self.UnknownCompartment

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

def startagent(sockpath):
    if not canexec('ssh-agent'):
        printerr("'Cannot execute 'ssh-agent'")
        exit(1)
    e = call(['ssh-agent', '-a', sockpath], stdout=DEVNULL)
    if e != 0:
        printerr('Unable to start ssh-agent on', sockpath)
        exit(e)

def addkeys(compartment, loaded_keynames):
    if loaded_keynames is None:
        return 2
    exitcode = 0
    for keyfile in compartment.keyfiles:
        (dir, file) = path.split(keyfile)
        if file in loaded_keynames:
            continue
        args = ['ssh-add', '-t', '10h']
        if compartment.confirm:
            args += ['-c']
            if not canexec('ssh-askpass'):
                printerr('WARNING: ssh-askpass not available but needed for'
                    ' compartment {}'.format(compartment.name))
        args += [file]
        if os.access(path.expanduser(keyfile), os.R_OK):
            e = call(args, cwd=path.expanduser(dir))
            if exitcode == 0: exitcode = e
        else:
            printerr('Cannot read keyfile: {}'.format(keyfile))
            if exitcode == 0: exitcode = 2
    return exitcode

def ckset(args, env):
    if len(args.params) > 1:
        printerr('Too many args: {}'.format(args.params))
        return 2
    elif len(args.params) == 1:
        namearg = args.params[0]
    else:
        namearg = None

    ck = CK(env)
    if namearg is None: compartment = ck.compartment_from_sock()
    else:               compartment = ck.compartment_named(namearg)
    if compartment == None:
        printerr('No compartment.')
        return 1
    elif compartment == CK.UnknownCompartment:
        printerr('Unknown compartment.')
        if not args.no_load:
            return 1    # We don't know a list of keys for this compartment.

    sockpath = ck.sockpath(namearg)
    keynames = fetch_keynames(sockpath)
    if keynames is None and (args.start or namearg is None):
        #   Start compartment. Not sure if we really want this print.
        printerr('Starting ssh-agent '
            f'for compartment {compartment.name} on {sockpath}')
        startagent(sockpath)
        keynames = fetch_keynames(sockpath)

    if namearg is not None:
        #   Given an arg, we change the compartment. We must change both
        #   the default socket for this process and SSH_AUTH_SOCK in the
        #   parent environment. We unset SSH_AGENT_PID because that's
        #   easier, though probably we should get the agent's PID and set
        #   it properly so that `ssh-agent -k` can be used.
        os.environ['SSH_AUTH_SOCK'] = str(sockpath)
        evalwrite('unset SSH_AGENT_PID=')
        evalwrite(f'export SSH_AUTH_SOCK={sockpath}')

    if not args.verbose:
        print(compartment.name)
    else:
        if keynames is None:
            print(compartment.name + ': stopped')
        else:
            print(compartment.name + ': running')
            for keyfile in compartment.keyfiles:
                (_, kn) = path.split(keyfile)
                if kn in keynames:
                    print(' ', kn + ':', 'loaded')
                else:
                    print(' ', kn + ':', 'absent')
    if not args.no_load:
        e = addkeys(compartment, keynames)
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
    arg('-c', '--config-file', default=CONFIG_FILE,
        help='config file to use, default {}'.format(CONFIG_FILE))
    arg('--eval-file',
        help='file to which to write commands for parent shell')
    arg('-n', '--no-load', action='store_true',
        help='Do not add configured but unloaded keys to the compartment.')
    arg('-s', '--start', action='store_true',
        help='If necessary, start agent for compartment'
            ' (automatic when compartment name given')
    arg('-v', '--verbose', action='store_true',
        help="print compartment's status and loaded keys")
    arg('--version', action='store_true', help='print version')
    arg('subcommand', help=' '.join(sorted(subcommands.keys())))
    arg('params', nargs='*')
    return p, subcommands

def main():
    global CONFIG_FILE, EVALFILE
    p, subcommands = argparser()
    args = p.parse_args()

    if args.version:
        print('version 0')
        sys.exit(0)

    CONFIG_FILE = args.config_file
    if args.eval_file:  EVALFILE = open(args.eval_file, 'wt')

    #   This is not really the right way to do subcommands; we should be using
    #   https://docs.python.org/3/library/argparse.html#sub-commands
    sys.exit(subcommands[args.subcommand](args, os.environ))

if __name__ == '__main__': main()
