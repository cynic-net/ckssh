load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

@test 'ckssh no params' {
    run bin/ckssh
    [ $status -eq 1 ]
    assert_equal "$output" "Write me!"
}
