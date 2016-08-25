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

@test "unit test mode" {
    assert_equal "$?" 0
}

@test 'meaning_of_life' {
    assert_equal $(meaning_of_life) 42
}

@test 'find_host_config no config file' {
    HOME="$BATS_TEST_DIRNAME/nonexistent"
    run find_host_config bob
    assert_failure 2
    assert_output ''
}

@test 'find_host_config unknown host' {
    run find_host_config nobody_I_know
    assert_failure 1
    assert_output ''
}

@test 'find_host_config bob' {
    run find_host_config bob
    assert_success
    assert_output <<___
CK_Compartment cjs@cynic.net
Host 192.168.1.1
X11Fowarding yes
___
}

@test 'find_compartment_config no_such_compartment' {
    run find_compartment_config no_such_compartment
    assert_failure
}

@test 'find_compartment_config cjs@cynic.net' {
    run find_compartment_config 'cjs@cynic.net'
    assert_success
    assert_output <<___
CK_Keyfile ~/.ssh/cjs@cynic.net-160819
CK_Keyfile ~/.ssh/cjs@cynic.net-120531
___
}
