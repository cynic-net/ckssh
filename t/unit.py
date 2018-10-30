from    io import StringIO
from    pathlib import Path
import  pytest

import  ckssh
from    ckssh import (
        runtimedir, Compartment, parseconfig, canexec, evalwrite, CK,
        )

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
    ck = CK({}, configfile=CONFIGFILE, compartment_path='/ckssh/')
    unknown = CK.UnknownCompartment
    cs = ck.compartment_from_sock

    assert None     == cs(None)
    assert unknown  == cs('/ckssh/socket/NOT_A_COMP')
    assert unknown  == cs('/NOTCK/socket/special')

    c = cs('/ckssh/socket/special')
    assert 'special' == c.name
    assert ['/special/special.priv'] == c.keyfiles

    c = cs('/ckssh/socket/cjs@cynic.net')
    assert 'cjs@cynic.net' == c.name
    assert [
        '/home/cjs/privkeys/cjs@cynic.net-160819',
        '~/.ssh/cjs@cynic.net-120531',
    ] == c.keyfiles

    c = cs('/ckssh/socket/empty')
    assert 'empty' == c.name

def test_canexec(capfd):
    assert canexec('which')
    assert ('', '') == capfd.readouterr()
    assert not canexec('a-program-which-certainly-does-not-exist')
    assert ('', '') == capfd.readouterr()

def test_evalwrite():
    ckssh.EVALFILE = StringIO()
    evalwrite('foo')
    assert 'foo\n' == ckssh.EVALFILE.getvalue()
