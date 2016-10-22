load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; source bin/ckssh; }
teardown() { teardown_bats_tmp; }


@test 'ckssh-add keys from command line' {
    ckssh_add cjs@cynic.net path/to/key1 'path/to/key 2'
    assert_equal "$SSH_AUTH_SOCK" "$XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net"
    assert_equal "${#keyfiles[@]}" 2
    assert_equal "${keyfiles[0]}" path/to/key1
    assert_equal "${keyfiles[1]}" 'path/to/key 2'
}

@test 'ckssh-add keys from config file' {
    ckssh_add cjs@cynic.net
    assert_equal "$SSH_AUTH_SOCK" "$XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net"
    assert_equal "${#keyfiles[@]}" 2
    assert_equal "${keyfiles[0]}" "/home/cjs/privkeys/cjs@cynic.net-160819"
    assert_equal "${keyfiles[1]}" "$HOME/.ssh/cjs@cynic.net-120531"
}
