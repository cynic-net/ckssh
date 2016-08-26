load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

setup() {
    # This should be part of the BATS framework
    export BATS_TMPDIR="$BATS_TEST_DIRNAME/.bats_tmp"
    mkdir -p -m 0700 "$BATS_TMPDIR"

    export HOME="$BATS_TEST_DIRNAME/mock_home"
    export XDG_RUNTIME_DIR="$BATS_TMPDIR/xdg_runtime"
    mkdir -p -m 0700 "$XDG_RUNTIME_DIR"

    source bin/ckssh
}

teardown() { rm -rf "$BATS_TMPDIR"; }


@test 'ckssh-add compartment by compartment name; 1 key from comand line' {
    ckssh_add cjs@cynic.net path/to/key
    assert_equal "$SSH_AUTH_SOCK" "$XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net"
    assert_equal "${#keyfiles[@]}" 1
    assert_equal "${keyfiles[0]}" path/to/key
}

@test 'ckssh-add compartment by hostalias; 2 keys from command line' {
    ckssh_add bob path/to/key1 'path/to/key 2'
    assert_equal "$SSH_AUTH_SOCK" "$XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net"
    assert_equal "${#keyfiles[@]}" 2
    assert_equal "${keyfiles[0]}" path/to/key1
    assert_equal "${keyfiles[1]}" 'path/to/key 2'
}
