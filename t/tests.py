from pathlib import Path
import pytest

from ckssh import *

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
    assert 2                == len(cs)

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

def test_sockpath():
    assert Path('/foo/socket/bar') \
        == CK(compartment_path='/foo/').sockpath('bar')
    assert Path('/foo/bar/socket/baz') \
        == CK(compartment_path=Path('/foo/bar')).sockpath('baz')

def test_compartment_name_default_params():
    assert CK().compartment_name()

@pytest.mark.parametrize('sock,expected', [
    [None,                              None],
    ['/ckssh/socket/NOT_A_COMP',        None],
    ['/NOTCK/socket/special',           None],
    ['/ckssh/socket/special',           'special'],
    ['/ckssh/socket/cjs@cynic.net',     'cjs@cynic.net'],
])
def test_compartment_name(sock, expected):
    ck = CK(configfile=CONFIGFILE, compartment_path='/ckssh/')
    assert expected == ck.compartment_name(sock)
