''' These "functional" tests go beyond unit tests in that they test
    things like argument parsing and output to `EVALFILE`.

    They do not call main() itself, run the code in a separate
    interpreter, or check that Bash code from EVALFILE is correctly
    executed by Bash. That's done to some degree by a minimal set of
    true functional tests in the top-level ``Test`` script.
'''
from    io import StringIO
from    pathlib import Path
import  ckssh

def main(subcommand, *, sockpath=None):
    ''' Run something similar to ckssh.main() in the test framework.
        Note that this runs in the existing process.
        EVALFILE is set to a fresh StringIO() so its output can be asserted.
    '''
    ckssh.EVALFILE = StringIO()
    TESTDIR = Path(__file__).parent
    TESTHOME = str(Path(TESTDIR, 'mock_home'))
    ENV = dict(
        HOME=TESTHOME,
        XDG_RUNTIME_DIR='/test-xdg-rtdir-nonexistent',
        )
    if sockpath: ENV['SSH_AUTH_SOCK'] = sockpath
    p, subcommands = ckssh.argparser()
    args = p.parse_args([subcommand])
    return subcommands[args.subcommand](args, ENV)

def test_print_bash_init():
    main('bash-init')
    assert 'ckset()' in ckssh.EVALFILE.getvalue()

def test_ckset_show_no_compartment(capsys):
    main('ckset')
    cap = capsys.readouterr()
    assert ('', 'ckssh: No compartment.\n') == (cap.out, cap.err)

def test_ckset_show_unknown_compartment(capsys):
    main('ckset', sockpath='/not/known')
    cap = capsys.readouterr()
    assert ('', 'ckssh: Unknown compartment.\n') == (cap.out, cap.err)

def test_ckset_show_compartment_name(capsys):
    main('ckset', sockpath='/test-xdg-rtdir-nonexistent/ckssh/socket/empty')
    cap = capsys.readouterr()
    assert ('empty\n', '') == (cap.out, cap.err)
