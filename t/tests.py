from ckssh import CK, parseconfig
from pathlib import Path
import pytest

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

def test_sockpath():
    assert Path('/foo/socket/bar') \
        == CK(compartment_path='/foo/').sockpath('bar')
    assert Path('/foo/bar/socket/baz') \
        == CK(compartment_path=Path('/foo/bar')).sockpath('baz')

def test_get_compartment():
    ck = CK(configfile=CONFIGFILE, compartment_path='/ckssh/')
    assert None            == ck.get_compartment('/ckssh/socket/NOT_A_COMP')
    assert None            == ck.get_compartment('/NOTCK/socket/special')
    assert 'special'       == ck.get_compartment('/ckssh/socket/special')
    assert 'cjs@cynic.net' == ck.get_compartment('/ckssh/socket/cjs@cynic.net')
