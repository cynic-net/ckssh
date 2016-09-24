load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; }
teardown() { teardown_bats_tmp; }


@test 'ckssh no params' {
    run bin/ckssh
    [ $status -eq 1 ]
    assert_equal "$output" "Write me!"
}
