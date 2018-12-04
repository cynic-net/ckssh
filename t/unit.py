' Unit Tests '

from    io import StringIO
from    os.path import dirname, join as opj
import  pytest
from    ckssh import ssh_bool, Compartment, Config

TESTDIR = dirname(__file__)
CONFIGFILE = opj(TESTDIR, 'mock_home/.ssh/ckssh_config')

def test_ssh_bool():
    for t in ['yes', 'true', 'trUE', True]:
        assert True is ssh_bool(t, 0)
    for f in ['no', 'false', False]:
        assert False is ssh_bool(f, 0)
    with pytest.raises(Config.ConfigError) as e:
        ssh_bool('0', 27)
    assert e.match(r'^Invalid boolean value on line 27: 0$')

def test_compartment():
    comp = Compartment('t')
    assert 't' == comp.name
    assert []  == comp.keyfiles
    assert True is comp.confirm()

    comp.set_confirm(False);
    assert False is comp.confirm()

    comp.set_confirm(True)
    assert False is comp.confirm()  # First setting takes precedence

    with pytest.raises(RuntimeError):
        comp.set_confirm(2)

def test_Config_load_empty():
    conf  = Config.load(StringIO())
    assert {} == conf.compartments

def test_Config_load():
    input = u'''
        CK_Compartment alice
        CK_Compartment bob@example.com
            CK_Keyfile /tmp/id_temp
            CK_Confirm false
            #   First value takes precedence
            CK_Confirm true
            SomeOtherParam ignored
        CK_Compartment charlie
        CK_Compartment bob@example.com
            CK_Keyfile ~/.ssh/id_rsa
    '''
    conf  = Config.load(StringIO(input))
    assert ['alice', 'bob@example.com', 'charlie'] \
        == sorted(conf.compartments.keys())

    alice = conf.compartments['alice']
    assert 'alice'              == alice.name
    assert []                   == alice.keyfiles
    assert True                 is alice.confirm()

    bob = conf.compartments['bob@example.com']
    assert 'bob@example.com'    == bob.name
    assert '/tmp/id_temp'       == bob.keyfiles[0]
    assert '~/.ssh/id_rsa'      == bob.keyfiles[1]
    assert 2                    == len(bob.keyfiles)
    assert False                is bob.confirm()

@pytest.mark.xfail(strict=True, desc='We need to write error handling.')
def test_Config_load_keywithoutvalue():
    with pytest.raises(Config.ConfigError) as e:
        Config.load(StringIO(u'CK_this_is_wrong'))
    assert e.match(r'^Unknown config parameter on line 1: ck_this_is_wrong$')

def test_Config_load_unknown_ckparam():
    input = u'''
        # Blank lines to check that line number of error is correct
        CK_ThisIsntAKnownParam false
        '''
    with pytest.raises(Config.ConfigError) as e:
        Config.load(StringIO(input))
    assert e.match('Unknown config parameter on line 3')

@pytest.mark.xfail(strict=True, desc='We need to write error handling.')
def test_Config_load_errors():
    #   Compartment config before a compartment name is given.
    Config.load(StringIO(u'CK_Confirm false'))

def test_t_config_file():
    with open(CONFIGFILE) as f:
        conf = Config.load(f)
    assert '~/.ssh/cjs@cynic.net-120531' \
        == conf.compartments['cjs@cynic.net'].keyfiles[1]
