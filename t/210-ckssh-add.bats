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


@test 'ckssh-add XDG_RUNTIME_DIR not set' {
    unset XDG_RUNTIME_DIR
    run bin/ckssh-add bob
    assert_failure
    assert_output '$XDG_RUNTIME_DIR not set.'
}

@test 'ckssh-add nonexistent host and compartment' {
    run bin/ckssh-add xyzzy
    assert_failure
    assert_output 'No config for host or compartment "xyzzy".'
}

@test 'ckssh-add host with nonexistent compartment' {
    run bin/ckssh-add david
    assert_failure
    assert_output \
        'Host "david" references nonexistent compartment "no_such_compartment".'
}