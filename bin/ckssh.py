#!/usr/bin/env python

from    __future__ import print_function
import  errno, os, re, socket
import  sys

py_major = sys.version_info[0]

####################################################################
#   SSH agent protocol

class SSHAgentProtoError(RuntimeError):
    pass

def read_agentproto_int(stream, length):
    bs = stream.read(length)
    if len(bs) != length:
        raise SSHAgentProtoError(
            'Short int (expected {}): {}'.format(length, bs))
    #   No `int.from_bytes()` in Python 2. :-(
    if py_major == 2:
        result = long(0)
    else:
        result = 0
    for c in bs:
        if not isinstance(c, int):
            #   Python 3 already returns int,
            #   but Python 2 return str of length 1.
            c = ord(c)
        result <<= 8
        result += c
    return result

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

def fetch_keynames(env=os.environ):
    sockname = env.get('SSH_AUTH_SOCK')
    if not sockname:
        return None
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(env.get('SSH_AUTH_SOCK'))
    except socket.error as ex:
        if ex.errno in (errno.ENOENT, errno.ECONNREFUSED):
            return None
        raise ex
    sock.sendall(b'\x00\x00\x00\x01'    # message length = 1
                 b'\x0b')               # SSH2_AGENTC_REQUEST_IDENTITIES
    #   !!! This shuts down both sides of the connection!
    #sock.shutdown(socket.SHUT_WR)
    comments = read_agentproto_idcomments(sock.makefile('rb'))
    sock.close()
    return comments

####################################################################
#   Configuration

def ssh_bool(s, lineno):
    ''' Parse an ssh_config-style boolean value.

        This isn't really defined anywhere, as far as I can tell
        (the manpages just use `yes` and `no`, though I'm sure that
        `true` and `false` are allowed), so I just pick a reasonable
        range of words that cannot be confused with some other kind
        of value (e.g., I don't accept 0 as false).
    '''
    if s is True :                      return True
    if s is False:                      return False
    if s.lower() in ('yes', 'true'):    return True
    if s.lower() in ('no', 'false'):    return False
    raise Config.ConfigError(
        'Invalid boolean value on line {}: {}'.format(lineno, s))

class Compartment():
    ' The configuration for a single compartment. '

    def __init__(self, name):
        self.name = name
        self.keyfiles = []
        self._confirm = None

    def confirm(self):
        ' Do we request confirmation when loading key into agent? '
        if self._confirm is None:
            return True             # unset
        return self._confirm

    def set_confirm(self, value):
        ' Set confirm value if not already set. '
        if value not in (False, True):
            raise RuntimeError('bad confirm value: {}'.format(repr(value)))
        if self._confirm is None:
            self._confirm = value

class Config():
    ' The compartments and other configuration read from the config file. '

    class ConfigError(RuntimeError):
        pass

    @staticmethod
    def load(input):
        parser = re.compile(r'(?:\s*)(\w+)(?:\s*=\s*|\s+)(.+)')
        conf = Config()
        compartments = conf.compartments
        curname = None
        lineno = 0
        for line in input:
            lineno += 1
            match = parser.match(line)
            if not match: continue
            key = match.group(1).lower(); value = match.group(2)
            if key == 'ck_compartment':
                curname = value
                compartments.setdefault(curname, Compartment(curname))
                continue
            if key == 'ck_keyfile':
                compartments[curname].keyfiles.append(value)
                continue
            if key == 'ck_confirm':
                compartments[curname].set_confirm(ssh_bool(value, lineno))
                continue
            if key == 'ck_host' or key == 'ck_compartmentname':
                #   Currently unimplemented.
                curname = None
                continue
            if key.startswith('ck_'):
                raise Config.ConfigError(
                    'Unknown config parameter on line {}: {}' \
                    .format(lineno, key))
            # All non-CK parameters are ignored.
        return conf

    def __init__(self):
        self.compartments = {}

if __name__ == '__main__':
    with open(os.path.expanduser('~/.ssh/ckssh_config')) as f:
        conf = Config.load(f)
    print(sorted(conf.compartments.keys()))
