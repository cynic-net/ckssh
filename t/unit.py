from    io import BytesIO, StringIO
from    binascii import unhexlify
from    pathlib import Path
import  pytest

import  ckssh
from    ckssh import (
        SSHAgentProtoError, read_agentproto_idcomments,
        runtimedir, Compartment, parseconfig, canexec, evalwrite, CK,
        )

####################################################################
#   SSH agent protocol

def test_ssh2_ids_answer_decode_0():
    answer0 = (
        0, 0, 0, 5,     # message length
        0xC,            # SSH2_AGENT_IDENTITIES_ANSWER
        0, 0, 0, 0,     # identities count: 0
    )
    assert [] == read_agentproto_idcomments(BytesIO(bytes(answer0)))

def test_ssh2_ids_answer_decode_2():
    answer2 = (
        b''
        b'\0\0\0\5'     # message length
        b'\x0C'         # SSH2_AGENT_IDENTITIES_ANSWER
        b'\0\0\0\2'     # identities count: 2

        b'\0\0\0\1'     # 1st answer blob length: 1
        b'\x7E'
        b'\0\0\0\3'     # 1st answer comment length: 3
        b'foo'

        b'\0\0\0\0'     # 2nd answer blob length: 0
        b''
        b'\0\0\0\7'     # 2nd answer comment length: 7
        b'bar baz'
    )
    assert ['foo', 'bar baz'] \
        == read_agentproto_idcomments(BytesIO(bytes(answer2)))

@pytest.mark.parametrize('badmsg', (
    '',
    '00000001',     # no response type
    '0000000102',   # bad response type
    '000000020C',   # bad length
    ))
def test_ssh2_ids_answer_decode_err(badmsg):
    bs = unhexlify(badmsg)  # Convert printable test param to bytes
    with pytest.raises(SSHAgentProtoError):
        read_agentproto_idcomments(BytesIO(bs))

####################################################################
#   ckssh stuff

TESTDIR = Path(__file__).parent
CONFIGFILE = Path(TESTDIR, 'mock_home/.ssh/ckssh_config')

def test_test_paths():
    assert TESTDIR.is_dir()
    assert CONFIGFILE.is_file()

def test_runtimedir():
    #   XDG_RUNTIME_DIR specified
    assert Path('/foo/ckssh') == runtimedir({'XDG_RUNTIME_DIR': '/foo'})

    #   Default runtime dir calculation
    #   This probably doesn't work under Windows.
    d = runtimedir({})
    assert             d.parts[0]   # root directory
    assert 'run'    == d.parts[1]
    assert 'user'   == d.parts[2]
    assert             d.parts[3]   # userid
    assert 'ckssh'  == d.parts[4]
    assert 5        == len(d.parts)

def test_runtimedir_heuristic():
    ' See comments in the function re the heuristics we use. '
    path = runtimedir({})
    root, run, user, uid, ckssh = path.parts
    assert '/'      == root
    assert 'run'    == run
    assert 'user'   == user
    assert 'ckssh'  == ckssh
    assert uid.isdecimal()

def test_compartment():
    c = Compartment('acomp', ['kf1', 'kf2'])
    assert 'acomp' == c.name
    assert ['kf1', 'kf2'] == c.keyfiles

def test_parseconfig():
    with open(str(CONFIGFILE)) as f:
        cs = parseconfig(f)

    assert 'cjs@cynic.net'              == cs[0].name
    assert [ '/home/cjs/privkeys/cjs@cynic.net-160819',
              '~/.ssh/cjs@cynic.net-120531',
        ]                               == cs[0].keyfiles
    assert True                         == cs[0].confirm

    assert 'special'                    == cs[1].name
    assert ['/special/special.priv']    == cs[1].keyfiles
    assert False                        == cs[1].confirm

    assert 'empty'                      == cs[2].name
    assert []                           == cs[2].keyfiles
    assert True                         == cs[2].confirm

    assert 3                            == len(cs)

def test_sockpath():
    assert Path('/foo/socket/bar') \
        == CK({}, compartment_path='/foo/').sockpath('bar')
    assert Path('/foo/bar/socket/baz') \
        == CK({}, compartment_path=Path('/foo/bar')).sockpath('baz')

def sockenv(path):
    return { 'SSH_AUTH_SOCK': path }

def test_conf_no_config():
    ck = CK({})
    assert None                  is ck.compartment_from_sock()
    assert CK.UnknownCompartment is ck.compartment_from_sock('/foo/bar')

def test_conf_with_config():
    ''' This tests the functions that lookup a compartment by asserting
        a compartment with the right name is returned. The full parsing
        of compartment values is tested in test_parseconfig() above.
    '''
    ck = CK({}, configfile=CONFIGFILE, compartment_path='/ckssh/')
    unknown = CK.UnknownCompartment
    cn = ck.compartment_named
    cs = ck.compartment_from_sock

    assert None             == cs(None)
    assert unknown          == cn('NOT_A_COMP')
    assert unknown          == cs('/ckssh/socket/NOT_A_COMP')
    assert unknown          == cs('/NOTCK/socket/special')

    assert 'special'        == cn('special').name
    assert 'special'        == cs('/ckssh/socket/special').name
    assert 'cjs@cynic.net'  == cn('cjs@cynic.net').name
    assert 'cjs@cynic.net'  == cs('/ckssh/socket/cjs@cynic.net').name
    assert 'empty'          == cn('empty').name
    assert 'empty'          == cs('/ckssh/socket/empty').name

def test_canexec(capfd):
    assert canexec('which')
    assert ('', '') == capfd.readouterr()
    assert not canexec('a-program-which-certainly-does-not-exist')
    assert ('', '') == capfd.readouterr()

def test_evalwrite():
    ckssh.EVALFILE = StringIO()
    evalwrite('foo')
    assert 'foo\n' == ckssh.EVALFILE.getvalue()
