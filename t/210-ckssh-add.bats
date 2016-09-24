load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; }
teardown() { teardown_bats_tmp; }


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
