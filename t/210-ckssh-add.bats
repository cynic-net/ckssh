load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; }
teardown() { teardown_bats_tmp; }


@test 'ckssh-add XDG_RUNTIME_DIR not set' {
    unset XDG_RUNTIME_DIR
    run bin/ckssh-add bob
    assert_failure
    assert_output '$XDG_RUNTIME_DIR not set.'
}

@test 'ckssh-add no compartment specified' {
    run bin/ckssh-add
    assert_failure
    assert_output 'Usage: ckssh-add <compartment-name>'
}

@test 'ckssh-add nonexistent compartment' {
    run bin/ckssh-add alice     # yes, this is a hostname
    assert_failure
    assert_output 'No config for compartment "alice".'
}

@test 'ckssh-add keys from command line' {
    run bin/ckssh-add cjs@cynic.net path/to/key1 'path/to/key 2'
    assert_output <<___
env SSH_AUTH_SOCK: $XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net
arg: -t
arg: 8h30m
arg: path/to/key1
env SSH_AUTH_SOCK: $XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net
arg: -t
arg: 8h30m
arg: path/to/key 2
export SSH_AUTH_SOCK=$XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net
___
    assert_success
}

@test 'ckssh-add keys from config file' {
    run bin/ckssh-add cjs@cynic.net
    assert_output <<___
env SSH_AUTH_SOCK: $XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net
arg: -t
arg: 8h30m
arg: /home/cjs/privkeys/cjs@cynic.net-160819
env SSH_AUTH_SOCK: $XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net
arg: -t
arg: 8h30m
arg: $HOME/.ssh/cjs@cynic.net-120531
export SSH_AUTH_SOCK=$XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net
___
    assert_success
}
