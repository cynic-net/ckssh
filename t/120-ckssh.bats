load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; source bin/ckssh; }
teardown() { teardown_bats_tmp; }


@test 'get_non_param_opts ssh' {
    run get_non_param_opts ssh
    assert_output --regexp '^[0-9A-Za-z]+$'
}

@test 'get_non_param_opts scp' {
    run get_non_param_opts scp
    assert_output --regexp '^[0-9A-Za-z]+$'
}

@test 'get_host_arg empty' {
    non_param_opts=12345ABCDEabcde
    host_arg=$(get_host_arg $non_param_opts)
    assert_equal "$host_arg" ''
}

@test 'get_host_arg' {
    non_param_opts=12345ABCDEabcde
    host_arg=$(get_host_arg $non_param_opts \
        -1 -x foo -A -y bar -b user@host:123 1 2)
    assert_equal "$host_arg" user@host:123
}
