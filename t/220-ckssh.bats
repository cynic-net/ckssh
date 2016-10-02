load 'ckssh-test-lib'

setup() { setup_bats_tmp; setup_mock_home; }
teardown() { teardown_bats_tmp; }


@test 'ckssh no params' {
    run bin/ckssh
    [ $status -eq 255 ]
    assert_equal "$output" "Usage: ckssh [ssh-options] hostname [command]"
}

@test 'ckscp no params' {
    run bin/ckscp
    [ $status -eq 255 ]
    assert_equal "$output" "Usage: ckscp [ssh-options] hostname [command]"
}
