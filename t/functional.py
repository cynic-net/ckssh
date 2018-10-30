from    collections import namedtuple as ntup
from    io import StringIO
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
    assert ('', 'No compartment.\n') == (cap.out, cap.err)
