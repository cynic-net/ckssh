load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; }
teardown() { teardown_bats_tmp; }


@test 'ckssh no params' {
    run bin/ckssh
    assert_failure 255
    assert_output "usage: ckssh [ssh-params ...] [user@]host [cmd...]"
}

@test 'ckssh host not found' {
    run bin/ckssh xyzzy
    assert_failure 255
    assert_output "ckssh: No config for host 'xyzzy'"
}

@test 'ckssh host has non-existant compartment' {
    run bin/ckssh david
    assert_failure 255
    assert_output "ckssh: No config for compartment 'no_such_compartment'"
}

@test 'ckssh ssh charles' {
    run bin/ckssh -o 'M1 m2' xyz@charles do 'more stuff' < <(echo 'Hi charles')
    assert_success
skip "Partially complete: now needs to do ckssh-add type thing "
    assert_output <<___
env SSH_AUTH_SOCK: $XDG_RUNTIME_DIR/ckssh/socket/special.priv
arg: -o
arg: M1 m2
arg: -o
arg: Protocol 2
arg: -o
arg: N1 value1
arg: -o
arg: N2 value2
arg: -o
arg: N3 value3
arg: -o
arg: Protocol 2
arg: xyz@charles
arg: do
arg: more stuff
stdin:
Hi charles
___
}
