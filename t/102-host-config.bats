load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; source bin/ckssh; }
teardown() { teardown_bats_tmp; }


@test "unit test mode" {
    assert_equal "$?" 0
}


@test 'print_host_config unknown host' {
    run print_host_config nobody_I_know
    assert_failure 1

    # Not that we care...
    assert_output 'Protocol 2
CK_SSHCommand ~/bin/mock-ssh'
}

@test 'print_host_config bob' {
    run print_host_config bob
    assert_success
    assert_output <<___
Protocol 2
CK_SSHCommand ~/bin/mock-ssh
CK_CompartmentName cjs@cynic.net
Host 192.168.1.1
X11Fowarding yes
___
}

@test 'print_host_config multiple' {
    run print_host_config charles
    assert_success
    assert_output <<___
Protocol 2
CK_SSHCommand ~/bin/mock-ssh
N1 value1
CK_CompartmentName special
N2 value2
CK_CompartmentName ignored
N3 value3
___
}

@test 'load_host_config no config file' {
    HOME="$BATS_TEST_DIRNAME/nonexistent"
    local -a a
    set +e; load_host_config bob; retval=$?; set -e
    assert_equal "${#a[@]}" 0
    assert_equal $retval 10
}

@test 'load_host_config no_such_host' {
    local -a a
    set +e; load_host_config no_such_host; retval=$?; set -e
    assert_equal "${#a[@]}" 0
    assert_equal $retval 1
}

@test 'load_host_config no_such_compartment' {
    local -a a
    set +e; load_host_config a david; retval=$?; set -e
    assert_equal $retval 2
}

@test 'load_host_config mulitple host section match' {
    local -a a
    a[2]='pre-existing data'    # Ensure array we pass in is left intact

    load_host_config a charles
    assert_success
    assert_equal "${a[2]}" 'pre-existing data'
    assert_equal "${a[3]}" 'Protocol 2'
    assert_equal "${a[4]}" 'CK_SSHCommand ~/bin/mock-ssh'
    assert_equal "${a[5]}" 'N1 value1'
    assert_equal "${a[6]}" 'N2 value2'
    assert_equal "${a[7]}" 'N3 value3'
    assert_equal "${a[8]}" 'Protocol 2' # Harmless repeat from compartment scan
    assert_equal "${a[9]}" 'CK_SSHCommand ~/bin/mock-ssh'
    assert_equal "${a[10]}" 'CK_Keyfile /special/special.priv'
    assert_equal "${#a[@]}" 9
}
