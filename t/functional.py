from    collections import namedtuple as ntup
from    io import StringIO
from    pathlib import Path
import  ckssh

Args = ntup('TestArgs', 'params, a')
Args.__new__.__defaults__ = ([], False)

def test_print_bash_init():
    ckssh.EVALFILE = StringIO()
    ckssh.print_bash_init(None, {})
    assert 'ckset()' in ckssh.EVALFILE.getvalue()

def test_ckset_show_no_compartment(capsys):
    ckssh.ckset(Args(), {})
    cap = capsys.readouterr()
    assert ('', 'ckssh: No compartment.\n') == (cap.out, cap.err)

TESTDIR = Path(__file__).parent
TESTHOME = str(Path(TESTDIR, 'mock_home'))

def test_ckset_show_unknown_compartment(capsys):
    ENV = dict(SSH_AUTH_SOCK='/not/known')
    ckssh.ckset(Args(), ENV)
    cap = capsys.readouterr()
    assert ('', 'ckssh: Unknown compartment.\n') == (cap.out, cap.err)

def test_ckset_show_compartment_name(capsys):
    ENV = dict(HOME=TESTHOME,
               XDG_RUNTIME_DIR='/test-xdg-rtdir-nonexistent',
               SSH_AUTH_SOCK='/test-xdg-rtdir-nonexistent/ckssh/socket/empty')
    ckssh.ckset(Args(), ENV)
    cap = capsys.readouterr()
    assert ('empty\n', '') == (cap.out, cap.err)
