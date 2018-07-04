from    io import StringIO
from    pathlib import Path
import  pytest

import  ckssh
from    ckssh import *


TESTDIR = Path(__file__).parent
CONFIGFILE = Path(TESTDIR, 'mock_home/.ssh/ckssh_config')

def test_test_paths():
    assert TESTDIR.is_dir()
    assert CONFIGFILE.is_file()

def test_parseconfig():
    with open(str(CONFIGFILE)) as f:
        cs = parseconfig(f)
    assert 'cjs@cynic.net'  == cs[0].name
    assert 'special'        == cs[1].name
    assert 'empty'          == cs[2].name
    assert 3                == len(cs)

def test_runtimedir():
    assert Path('/foo/ckssh') == runtimedir({'XDG_RUNTIME_DIR': '/foo'})
    assert 'ckssh' == runtimedir({}).name
    assert 'ckssh' == runtimedir().name     # Has a default env argument

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
    assert 'cjs@cynic.net'  == cs[0].name
    assert 'special'        == cs[1].name
    assert 'empty'          == cs[2].name
    assert 3                == len(cs)

def test_sockpath():
    assert Path('/foo/socket/bar') \
        == CK(compartment_path='/foo/').sockpath('bar')
    assert Path('/foo/bar/socket/baz') \
        == CK(compartment_path=Path('/foo/bar')).sockpath('baz')

def test_conf_default_params():
    assert CK().compartment_from_sock()

def test_conf():
    ck = CK(configfile=CONFIGFILE, compartment_path='/ckssh/')
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

def test_evalwrite():
    ckssh.EVALFILE = StringIO()
    evalwrite('foo')
    assert 'foo\n' == ckssh.EVALFILE.getvalue()

def test_print_bash_init():
    ckssh.EVALFILE = StringIO()
    ckssh.print_bash_init(None)
    assert 'ckset()' in ckssh.EVALFILE.getvalue()


Args = ntup('TestArgs', 'params, a')
Args.__new__.__defaults__ = ([], False)

def test_ckset_show(capsys):
    ckset(Args())
    cap = capsys.readouterr()
    assert 'cynic\n' == cap.out
    assert '' == cap.err
