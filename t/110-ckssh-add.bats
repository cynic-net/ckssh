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


@test 'ckssh-add compartment by compartment name' {
    run bin/ckssh-add cjs@cynic.net
    assert_success
    assert_output \
        "export SSH_AUTH_SOCK=$XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net"
}

@test 'ckssh-add compartment by hostalias' {
    run bin/ckssh-add bob
    assert_success
    assert_output \
        "export SSH_AUTH_SOCK=$XDG_RUNTIME_DIR/ckssh/socket/cjs@cynic.net"
}
