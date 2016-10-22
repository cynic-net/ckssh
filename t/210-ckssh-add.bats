load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; }
teardown() { teardown_bats_tmp; }


@test 'ckssh-add XDG_RUNTIME_DIR not set' {
    unset XDG_RUNTIME_DIR
    run bin/ckssh-add bob
    assert_failure
    assert_output '$XDG_RUNTIME_DIR not set.'
}

@test 'ckssh-add no compartment specified' {
    run bin/ckssh-add
    assert_failure
    assert_output 'Usage: ckssh-add <compartment-name>'
}

@test 'ckssh-add nonexistent compartment' {
    run bin/ckssh-add alice     # yes, this is a hostname
    assert_failure
    assert_output 'No config for compartment "alice".'
}
