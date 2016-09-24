load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

setup_bats_tmp() {
    # This should be part of the BATS framework
    export BATS_TMPDIR="$BATS_TEST_DIRNAME/.bats_tmp"
    mkdir -p -m 0700 "$BATS_TMPDIR"
}

setup_mock_home() {
    export HOME="$BATS_TEST_DIRNAME/mock_home"
    export XDG_RUNTIME_DIR="$BATS_TMPDIR/xdg_runtime"
    mkdir -p -m 0700 "$XDG_RUNTIME_DIR"
}

teardown_bats_tmp() { rm -rf "$BATS_TMPDIR"; }
