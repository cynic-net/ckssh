load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

setup() {
    # This should be part of the BATS framework
    export BATS_TMPDIR="$BATS_TEST_DIRNAME/.bats_tmp"
    mkdir -p -m 0700 "$BATS_TMPDIR"

    export HOME="$BATS_TEST_DIRNAME/mock_home"
    export XDG_RUNTIME_DIR="$BATS_TMPDIR/xdg_runtime"
    mkdir -p -m 0700 "$XDG_RUNTIME_DIR"
}

teardown() { rm -rf "$BATS_TMPDIR"; }

@test 'ckssh no params' {
    run bin/ckssh
    [ $status -eq 1 ]
    assert_equal "$output" "Write me!"
}

@test 'ckssh-add XDG_RUNTIME_DIR not set' {
    unset XDG_RUNTIME_DIR
    run bin/ckssh-add bob
    assert_failure
    assert_output '$XDG_RUNTIME_DIR not set.'
}

@test 'ckssh-add nonexistent compartment' {
    run bin/ckssh-add xyzzy
    assert_failure
    assert_output "No config for host or compartment xyzzy"
}

@test 'ckssh-add compartment by compartment name' {
    skip "Coming in the next commit...."
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
