load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; source bin/ckssh; }
teardown() { teardown_bats_tmp; }


@test "unit test mode" {
    assert_equal "$?" 0
}


@test 'print_compartment_config no config file' {
    HOME="$BATS_TEST_DIRNAME/nonexistent"
    run print_compartment_config bob
    assert_failure 2
    assert_output ''
}

@test 'print_compartment_config no_such_compartment' {
    run print_compartment_config no_such_compartment
    assert_failure
}

@test 'print_compartment_config cjs@cynic.net' {
    run print_compartment_config 'cjs@cynic.net'
    assert_success
    assert_output <<___
Protocol 2
CK_Keyfile /home/cjs/privkeys/cjs@cynic.net-160819
CK_Keyfile ~/.ssh/cjs@cynic.net-120531
Compression yes
___
}

@test 'load_compartment_config no config file' {
    HOME="$BATS_TEST_DIRNAME/nonexistent"
    local -a a
    set +e; load_compartment_config bob; retval=$?; set -e
    assert_equal "${#a[@]}" 0
    assert_equal $retval 2
}

@test 'load_compartment_config no_such_compartment' {
    local -a a
    set +e; load_compartment_config no_such_compartment; retval=$?; set -e
    assert_equal "${#a[@]}" 0
    assert_equal $retval 1
}

@test 'load_compartment_config cjs@cynic.net' {
    local -a a
    load_compartment_config a 'cjs@cynic.net'
    assert_success
    assert_equal "${a[0]}" 'Protocol 2'
    assert_equal "${a[1]}" 'CK_Keyfile /home/cjs/privkeys/cjs@cynic.net-160819'
    assert_equal "${a[2]}" 'CK_Keyfile ~/.ssh/cjs@cynic.net-120531'
    assert_equal "${a[3]}" 'Compression yes'
    assert_equal "${#a[@]}" 4
}
