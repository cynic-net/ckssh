
load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

@test "pass" {
    assert true
    refute false
}
